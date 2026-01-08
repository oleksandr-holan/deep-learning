# %% [markdown]
# # Лабораторна робота 11
# ## Тема: Розпізнавання обличчя людей на фотографії
# 
# **Мета:** Навчитися верифікації людини на фотографії за допомогою попередньо навченої згорткової нейронної мережі та бібліотеки dlib.

# %% [markdown]
# ## 1. Підготовка (Setup)
# 
# ### Встановлення dlib (для Google Colab)
# 
# Для встановлення dlib може знадобитися встановлення системних залежностей, таких як `cmake`.

# %%
# Встановлення необхідних бібліотек у Colab/Anaconda
# У Colab це може зайняти кілька хвилин
!pip install dlib numpy scikit-image

# Завантаження попередньо навчених моделей dlib
# Ці файли мають бути розпаковані та знаходитися у робочій директорії
import os

model_dir = "." # Каталог для моделей

# Модель для виділення 68 ключових точок обличчя
url_landmarks = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
filename_landmarks = os.path.join(model_dir, "shape_predictor_68_face_landmarks.dat")

# Модель для виділення дескрипторів обличчя (ResNet)
url_face_rec = "http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2"
filename_face_rec = os.path.join(model_dir, "dlib_face_recognition_resnet_model_v1.dat")

if not os.path.exists(filename_landmarks):
    print(f"Завантаження {os.path.basename(filename_landmarks)}.bz2...")
    !curl -L -o {filename_landmarks}.bz2 {url_landmarks}
    !bzip2 -dk {filename_landmarks}.bz2
    
if not os.path.exists(filename_face_rec):
    print(f"Завантаження {os.path.basename(filename_face_rec)}.bz2...")
    !curl -L -o {filename_face_rec}.bz2 {url_face_rec}
    !bzip2 -dk {filename_face_rec}.bz2
    
print("Підготовка завершена.")

# %% [markdown]
# ## 2. Імпорт модулів та Завантаження моделей
# 
# Імпортуємо dlib та необхідні функції для роботи з зображеннями.

# %%
import dlib
import numpy as np
from skimage import io
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt

# Створюємо детектор обличчя (HOG-детектор)
face_detector = dlib.get_frontal_face_detector()

# Створюємо модель для визначення 68 ключових точок обличчя
shape_predictor = dlib.shape_predictor(filename_landmarks)

# Створюємо модель для вилучення дескрипторів обличчя (128-D вектор)
face_recognizer = dlib.face_recognition_model_v1(filename_face_rec)

print("Модулі імпортовані та моделі завантажені.")

# %% [markdown]
# ## 3. Обробка першого фото
# 
# Завантажуємо першу фотографію, знаходимо обличчя та вилучаємо його дескриптор.
# 
# **Примітка:** Замініть 'photo1.jpg' на реальний шлях до вашого файлу.

# %%
# Завантаження тестових зображень

image_filenames = ["photo1.png", "photo2.png"]
for i in image_filenames:
    !wget -nc https://raw.githubusercontent.com/oleksandr-holan/deep-learning/refs/heads/master/lab11/test_images/{i} -P ./uploaded_files

# %%
# Завантаження першої фотографії
try:
    img1 = io.imread('./uploaded_files/photo1.png')
    print("Фотографія 1 завантажена.")
except FileNotFoundError:
    print("ПОМИЛКА: Файл 'photo1.png' не знайдено. Будь ласка, завантажте його.")
    # Створюємо фіктивне зображення для запобігання помилці
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)

if img1.ndim == 3 and img1.shape[2] == 4:
    # Якщо 4 канали (RGBA), обрізаємо до RGB (3 канали)
    img1 = img1[:, :, :3]
    print("Зображення конвертовано з RGBA у RGB.")
    
if img1.dtype != np.uint8:
    # Конвертуємо до 8-бітного формату, якщо інший
    # Примітка: якщо це 16-бітне зображення, може знадобитися додаткова нормалізація, 
    # але для стандартних JPEG/PNG достатньо конвертації типу:
    img1 = img1.astype(np.uint8)
    print("Тип даних зображення конвертовано у np.uint8.") 

if not img1.flags['C_CONTIGUOUS']:
    img1 = np.ascontiguousarray(img1)
    print("Масив зображення зроблено C-неперервним.")

# Знаходимо обличчя на фотографії 1
detections1 = face_detector(img1, 1)

if len(detections1) == 0:
    print("Обличчя не знайдено на фотографії 1.")
    descriptor1 = None
else:
    # Використовуємо перше знайдене обличчя
    face_rect1 = detections1[0]
    
    # Виділяємо ключові точки
    shape1 = shape_predictor(img1, face_rect1)
    
    # Вилучаємо дескриптор обличчя (128-D вектор)
    descriptor1 = face_recognizer.compute_face_descriptor(img1, shape1)
    
    # Друкуємо дескриптор (перетворюємо у numpy масив для зручності друку)
    print("\nДескриптор обличчя 1 (перші 5 елементів):")
    print(np.array(descriptor1)[:5])
    print(f"Знайдено облич: {len(detections1)}")
    
    # Відображення фотографії з рамкою (опціонально, використовуємо matplotlib для Colab)
    plt.figure(figsize=(8, 4))
    plt.imshow(img1)
    plt.title("Фотографія 1")
    # Малюємо прямокутник навколо обличчя
    plt.gca().add_patch(plt.Rectangle((face_rect1.left(), face_rect1.top()), 
                                      face_rect1.width(), face_rect1.height(),
                                      edgecolor='r', facecolor='none', lw=2))
    plt.show()


# %% [markdown]
# ## 4. Обробка другого фото
# 
# Завантажуємо другу фотографію, знаходимо обличчя та вилучаємо його дескриптор.
# 
# **Примітка:** Замініть 'photo2.jpg' на реальний шлях до вашого файлу.

# %%
# Завантаження другої фотографії
try:
    img2 = io.imread('./uploaded_files/photo2.png')
    print("Фотографія 2 завантажена.")
except FileNotFoundError:
    print("ПОМИЛКА: Файл 'photo2.png' не знайдено. Будь ласка, завантажте його.")
    exit(1)

# Знаходимо обличчя на фотографії 2
detections2 = face_detector(img2, 1)

if len(detections2) == 0:
    print("Обличчя не знайдено на фотографії 2.")
    descriptor2 = None
else:
    # Використовуємо перше знайдене обличчя
    face_rect2 = detections2[0]
    
    # Виділяємо ключові точки
    shape2 = shape_predictor(img2, face_rect2)
    
    # Вилучаємо дескриптор обличчя (128-D вектор)
    descriptor2 = face_recognizer.compute_face_descriptor(img2, shape2)
    
    # Друкуємо дескриптор (перетворюємо у numpy масив для зручності друку)
    print("\nДескриптор обличчя 2 (перші 5 елементів):")
    print(np.array(descriptor2)[:5])
    print(f"Знайдено облич: {len(detections2)}")
    
    # Відображення фотографії з рамкою
    plt.figure(figsize=(8, 4))
    plt.imshow(img2)
    plt.title("Фотографія 2")
    # Малюємо прямокутник навколо обличчя
    plt.gca().add_patch(plt.Rectangle((face_rect2.left(), face_rect2.top()), 
                                      face_rect2.width(), face_rect2.height(),
                                      edgecolor='g', facecolor='none', lw=2))
    plt.show()

# %% [markdown]
# ## 5. Порівняння дескрипторів та верифікація
# 
# Обчислюємо евклідову відстань між дескрипторами. Згідно з рекомендацією **dlib**, поріг для верифікації (одна і та ж особа) становить **0,6**.

# %%
if descriptor1 is not None and descriptor2 is not None:
    # Обчислення евклідової відстані
    distance = euclidean(np.array(descriptor1), np.array(descriptor2))
    
    # Поріг
    VERIFICATION_THRESHOLD = 0.6
    
    print("\n--- Результати Верифікації ---")
    print(f"Евклідова відстань між дескрипторами: {distance:.4f}")
    print(f"Поріг dlib для верифікації: {VERIFICATION_THRESHOLD}")
    
    # Прийняття рішення
    if distance < VERIFICATION_THRESHOLD:
        print("ВЕРДИКТ: Відстань МЕНШЕ порогу. Ймовірно, на фотографіях ЗОБРАЖЕНА ОДНА ЛЮДИНА.")
    else:
        print("ВЕРДИКТ: Відстань БІЛЬШЕ порогу. Ймовірно, на фотографіях ЗОБРАЖЕНІ РІЗНІ ЛЮДИ.")
else:
    print("\nНеможливо провести порівняння, оскільки на одній або обох фотографіях не знайдено обличчя.")

# %% [markdown]
# ## 6. Експериментальні дослідження та висновки
# 
# **Завдання для самостійного виконання (опис у звіті):**
# 
# 1.  Проведіть експерименти, порівнюючи фотографії однієї людини та різних людей.
# 2.  Спробуйте знайти фотографії дуже схожих, але різних осіб, і порівняти їх.
# 3.  Зробіть власні фотографії з різних ракурсів, з різним поворотом/нахилом голови і протестуйте модель.
#     *   **Питання для аналізу:** Чи збільшується евклідова відстань? Чи правильно модель визначає, що це одна й та сама людина?
# 4.  Знайдіть фотографію однієї людини різного віку або зі значними змінами зачіски/зовнішності (борода, вуса, окуляри).
#     *   **Питання для аналізу:** Чи правильно визначає модель, що це одна й та сама людина?
# 5.  (Додатково) Спробуйте поекспериментувати з бібліотекою [OpenFace](https://cmusatyalab.github.io/openface/).
# 
# **Висновок:** Сформулюйте висновки до лабораторної роботи, аналізуючи отримані результати, особливо поріг верифікації та вплив зовнішніх факторів (ракурс, вік, зачіска) на евклідову відстань.
