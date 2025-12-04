# %% [markdown]
# # Лабораторна робота 10.3 (Extended Experiments)
# ## Тема: Advanced Transfer Learning & Fine Tuning
# 
# **Мета:** Провести серію експериментів з різними архітектурами, глибиною розморожування шарів та параметрами аугментації, спираючись на попередні успішні результати (Lab 08).
# 
# **Датасет:** 2000 train, 500 val, 500 test (per class).

# %% [markdown]
# ## 1. Підготовка даних (Setup)

# %%
import os
import random
import shutil
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Завантаження даних
if not os.path.exists('cats_dogs.zip'):
    !curl -L -o ./cats_dogs.zip https://www.kaggle.com/api/v1/datasets/download/bhavikjikadara/dog-and-cat-classification-dataset
    !unzip -q cats_dogs.zip

# Підготовка директорій
base_dir = "./PetImages_Lab10"
if os.path.exists(base_dir):
    shutil.rmtree(base_dir)
os.mkdir(base_dir)

dirs = ['training', 'validation', 'testing']
classes = ['cats', 'dogs']

for d in dirs:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)
    for c in classes:
        os.makedirs(os.path.join(base_dir, d, c), exist_ok=True)

# Функція спліту (2000 / 500 / 500)
def split_data(SOURCE, TRAINING, VALIDATION, TESTING, TRAIN_SIZE=2000, VAL_SIZE=500, TEST_SIZE=500):
    files = [f for f in os.listdir(SOURCE) if os.path.getsize(os.path.join(SOURCE, f)) > 0]
    
    if len(files) < (TRAIN_SIZE + VAL_SIZE + TEST_SIZE):
        print(f"Not enough images in {SOURCE}")
        return

    random.sample(files, len(files)) # Shuffle
    random.shuffle(files)
    
    train_files = files[:TRAIN_SIZE]
    val_files = files[TRAIN_SIZE:TRAIN_SIZE+VAL_SIZE]
    test_files = files[TRAIN_SIZE+VAL_SIZE:TRAIN_SIZE+VAL_SIZE+TEST_SIZE]

    for f in train_files: shutil.copyfile(os.path.join(SOURCE, f), os.path.join(TRAINING, f))
    for f in val_files: shutil.copyfile(os.path.join(SOURCE, f), os.path.join(VALIDATION, f))
    for f in test_files: shutil.copyfile(os.path.join(SOURCE, f), os.path.join(TESTING, f))

split_data("./PetImages/Cat/", f"{base_dir}/training/cats", f"{base_dir}/validation/cats", f"{base_dir}/testing/cats")
split_data("./PetImages/Dog/", f"{base_dir}/training/dogs", f"{base_dir}/validation/dogs", f"{base_dir}/testing/dogs")

print("Data processing complete.")

# %% [markdown]
# ## 2. Універсальна функція для експериментів
# Ця функція дозволяє нам запускати різні конфігурації без дублювання коду.

# %%
def run_experiment(name, base_model_class, target_size, preprocess_func, 
                   dropout_rate, unfreeze_from_layer_name=None, 
                   augment_type='standard', optimizer_type='rmsprop'):
    
    print(f"\n{'='*20}\nSTARTING EXPERIMENT: {name}\n{'='*20}")
    
    # 1. Налаштування аугментації
    if augment_type == 'standard':
        train_datagen = ImageDataGenerator(
            preprocessing_function=preprocess_func,
            rotation_range=30, width_shift_range=0.2, height_shift_range=0.2,
            shear_range=0.2, zoom_range=0.2, horizontal_flip=True, fill_mode='nearest'
        )
    elif augment_type == 'strong':
        train_datagen = ImageDataGenerator(
            preprocessing_function=preprocess_func,
            rotation_range=40, width_shift_range=0.2, height_shift_range=0.2,
            shear_range=0.2, zoom_range=0.3, horizontal_flip=True, 
            brightness_range=[0.7, 1.3], channel_shift_range=20.0, fill_mode='nearest'
        )
        
    test_datagen = ImageDataGenerator(preprocessing_function=preprocess_func)

    train_gen = train_datagen.flow_from_directory(
        f"{base_dir}/training", target_size=target_size, batch_size=32, class_mode='binary'
    )
    val_gen = test_datagen.flow_from_directory(
        f"{base_dir}/validation", target_size=target_size, batch_size=32, class_mode='binary'
    )
    test_gen = test_datagen.flow_from_directory(
        f"{base_dir}/testing", target_size=target_size, batch_size=32, class_mode='binary', shuffle=False
    )

    # 2. Побудова моделі (Feature Extraction)
    base_model = base_model_class(weights='imagenet', include_top=False, input_shape=target_size+(3,))
    base_model.trainable = False
    
    x = base_model.output
    # Використовуємо GlobalAveragePooling для сучасних моделей, Flatten для VGG (історично)
    if 'VGG' in name:
        x = layers.Flatten()(x)
        x = layers.Dense(256, activation='relu')(x)
    else:
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(512, activation='relu')(x)
        
    x = layers.Dropout(dropout_rate)(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)
    model = models.Model(inputs=base_model.input, outputs=outputs)

    # Вибір оптимізатора
    if optimizer_type == 'adam':
        opt = optimizers.Adam(learning_rate=0.001)
    else:
        opt = optimizers.RMSprop(learning_rate=0.0001)

    model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy'])
    
    print(f"--- Phase 1: Training Head ({name}) ---")
    hist_phase1 = model.fit(train_gen, epochs=6, validation_data=val_gen, verbose=1)

    # 3. Fine Tuning
    if unfreeze_from_layer_name:
        print(f"--- Phase 2: Fine Tuning ({name}) ---")
        base_model.trainable = True
        set_trainable = False
        
        # Логіка розморожування
        for layer in base_model.layers:
            if layer.name == unfreeze_from_layer_name:
                set_trainable = True
            if set_trainable:
                # Для ResNet не розморожуємо BatchNormalization шари (це важливо!)
                if 'BatchNormalization' in layer.__class__.__name__:
                    layer.trainable = False
                else:
                    layer.trainable = True
            else:
                layer.trainable = False
        
        # Компілюємо з низьким LR
        model.compile(
            optimizer=optimizers.RMSprop(learning_rate=1e-5), # Low LR is key
            loss='binary_crossentropy', 
            metrics=['accuracy']
        )
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2)
        ]

        hist_phase2 = model.fit(train_gen, epochs=15, validation_data=val_gen, callbacks=callbacks, verbose=1)
        
        # Об'єднуємо історію для графіка
        for k in hist_phase1.history.keys():
            hist_phase1.history[k].extend(hist_phase2.history[k])

    # 4. Оцінка
    print(f"--- Evaluating ({name}) ---")
    loss, acc = model.evaluate(test_gen)
    print(f"Test Accuracy: {acc*100:.2f}%")

    return hist_phase1, acc

# %% [markdown]
# ## Експеримент 1: VGG16 (Shallow Fine-Tuning)
# *   **Параметри:** Dropout 0.5 (з Lab 08), RMSprop.
# *   **FT:** Розморожуємо тільки останній **block5_conv1**.

# %%
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input as vgg_prep

hist_vgg_shallow, acc_vgg_shallow = run_experiment(
    name="Exp 1: VGG16 Shallow FT",
    base_model_class=VGG16,
    target_size=(150, 150),
    preprocess_func=vgg_prep,
    dropout_rate=0.5,
    unfreeze_from_layer_name='block5_conv1'
)

# %% [markdown]
# ## Експеримент 2: VGG16 (Deep Fine-Tuning)
# *   **Параметри:** Ті самі, що в Експ 1.
# *   **FT:** Розморожуємо глибше -> з **block4_conv1**. Це дозволить моделі змінити уявлення про більш абстрактні форми, а не тільки деталі.

# %%
hist_vgg_deep, acc_vgg_deep = run_experiment(
    name="Exp 2: VGG16 Deep FT",
    base_model_class=VGG16,
    target_size=(150, 150),
    preprocess_func=vgg_prep,
    dropout_rate=0.5,
    unfreeze_from_layer_name='block4_conv1'
)

# %% [markdown]
# ## Експеримент 3: InceptionV3 (Standard)
# *   **Параметри:** Dropout 0.2 (показав себе найкраще в Lab 08 для цієї моделі).
# *   **FT:** Розморожуємо з шару `mixed7` (стандартна практика для Inception).

# %%
from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input as inc_prep

hist_inc_std, acc_inc_std = run_experiment(
    name="Exp 3: InceptionV3 Standard",
    base_model_class=InceptionV3,
    target_size=(150, 150), # Inception може працювати і на 150, хоча любить 299
    preprocess_func=inc_prep,
    dropout_rate=0.2,
    unfreeze_from_layer_name='mixed7' 
)

# %% [markdown]
# ## Експеримент 4: InceptionV3 (Strong Augmentation)
# *   **Гіпотеза:** Inception — дуже потужна модель. Можливо, стандартна аугментація для неї занадто проста, і вона перенавчається?
# *   **Зміни:** Додаємо `brightness_range` та сильніший зум.

# %%
hist_inc_aug, acc_inc_aug = run_experiment(
    name="Exp 4: InceptionV3 Strong Aug",
    base_model_class=InceptionV3,
    target_size=(150, 150),
    preprocess_func=inc_prep,
    dropout_rate=0.2,
    unfreeze_from_layer_name='mixed7',
    augment_type='strong'
)

# %% [markdown]
# ## Експеримент 5: ResNet50V2 (Adam Optimizer)
# *   **Модель:** ResNet50**V2** (має кращу збіжність при FT ніж V1).
# *   **Зміни:** Використовуємо оптимізатор **Adam** замість RMSprop для етапу Feature Extraction. Adam часто дає швидший старт.
# *   **FT:** Розморожуємо останній блок `conv5_block1_preact_bn`.

# %%
from tensorflow.keras.applications.resnet_v2 import ResNet50V2, preprocess_input as res_prep

hist_res_adam, acc_res_adam = run_experiment(
    name="Exp 5: ResNet50V2 Adam",
    base_model_class=ResNet50V2,
    target_size=(150, 150),
    preprocess_func=res_prep,
    dropout_rate=0.2,
    unfreeze_from_layer_name='conv5_block1_preact_bn',
    optimizer_type='adam'
)

# %% [markdown]
# ## Експеримент 6: ResNet50V2 (Deep Fine-Tuning)
# *   **Гіпотеза:** ResNet дуже глибока. Розморозимо більше блоків.
# *   **FT:** Старт розморозки з `conv4_block1_preact_bn`.

# %%
hist_res_deep, acc_res_deep = run_experiment(
    name="Exp 6: ResNet50V2 Deep FT",
    base_model_class=ResNet50V2,
    target_size=(150, 150),
    preprocess_func=res_prep,
    dropout_rate=0.2,
    unfreeze_from_layer_name='conv4_block1_preact_bn',
    optimizer_type='rmsprop' # Повернемо RMSprop для порівняння стабільності
)

# %% [markdown]
# ## 3. Порівняння результатів та Візуалізація

# %%
def plot_histories(histories, titles):
    plt.figure(figsize=(20, 10))
    
    # Accuracy Plot
    plt.subplot(1, 2, 1)
    for hist, title in zip(histories, titles):
        plt.plot(hist.history['val_accuracy'], label=title)
    plt.title('Validation Accuracy Comparison')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)

    # Loss Plot
    plt.subplot(1, 2, 2)
    for hist, title in zip(histories, titles):
        plt.plot(hist.history['val_loss'], label=title)
    plt.title('Validation Loss Comparison')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.show()

# Збір всіх історій
all_hists = [hist_vgg_shallow, hist_vgg_deep, hist_inc_std, hist_inc_aug, hist_res_adam, hist_res_deep]
all_titles = ['VGG Shallow', 'VGG Deep', 'Inception Std', 'Inception Aug', 'ResNet Adam', 'ResNet Deep']
all_accs = [acc_vgg_shallow, acc_vgg_deep, acc_inc_std, acc_inc_aug, acc_res_adam, acc_res_deep]

plot_histories(all_hists, all_titles)

# Підсумкова таблиця
print("\n" + "="*50)
print(f"{'EXPERIMENT NAME':<30} | {'TEST ACCURACY':<10}")
print("-" * 50)
for title, acc in zip(all_titles, all_accs):
    print(f"{title:<30} | {acc*100:.2f}%")
print("="*50)

# %% [markdown]
# # Аналіз результатів (Template for Report)
# 
# ### 1. Вплив глибини розморожування (Deep vs Shallow FT)
# *   **VGG16:** Порівнюючи Exp 1 та Exp 2. Чи дало розморожування 4-го блоку приріст точності? Зазвичай для VGG це допомагає, оскільки вона має простішу ієрархію ознак.
# *   **ResNet:** Порівнюючи Exp 5 та Exp 6. Чи не призвело занадто глибоке розморожування до "catastrophic forgetting" (погіршення результатів) або перенавчання?
# 
# ### 2. Аугментація
# *   В Exp 4 ми використали сильну аугментацію для InceptionV3. Чи стала валідаційна точність більш плавною? Чи зменшився розрив між train та val loss (overfitting)?
# 
# ### 3. Порівняння архітектур
# *   В Lab 08 VGG16 відставала. Чи вдалося за допомогою Fine Tuning наблизити її до ResNet/Inception?
# *   Яка модель виявилася найшвидшою у навчанні і найстабільнішою?
# 
# ### 4. Оптимізатори
# *   Як показав себе Adam (Exp 5) порівняно з RMSprop? Чи швидше він досяг плато?