# Docs

## VGG16

steps 50
batch size 20
dropout 0.5

![alt text](image.png)
![alt text](image-1.png)

steps 50
batch size 20
dropout 0.8
![alt text](image-2.png)
![alt text](image-3.png)

steps 50
batch size 20
dropout 0.2

![alt text](image-4.png)
![alt text](image-5.png)

## InceptionV3

steps 50
batch size 16
dropout 0.5
learning_rate 1e-5

![alt text](Untitled.png)

steps 50
batch size 16
dropout 0.8
learning_rate 1e-5

![alt text](Untitled-1-1.png)

steps 50
batch size 16
dropout 0.2
learning_rate 1e-5

![alt text](Untitled-2.png)

## Resnet

steps 50
batch size 16
dropout 0.5
learning_rate 2e-5
epochs 15
validation_steps 25

![alt text](Untitled-3.png)

steps 50
batch size 16
dropout 0.2
learning_rate 2e-5
epochs 15
validation_steps 25

![alt text](Untitled-4.png)

steps 50
batch size 16
dropout 0.8
learning_rate 2e-5
epochs 15
validation_steps 25

![alt text](Untitled-5.png)

| Модель | Найкраща точність на валідації | Стабільність | Ознаки перенавчання? | Загальні нотатки |
| :--- | :--- | :--- | :--- | :--- |
| VGG16 | ~89% (при Dropout 0.2) | Досить стабільна | Легке перенавчання після 20 епох. | Проста, але потужна базова модель. Демонструє класичний компроміс у регуляризації. |
| ResNet50 | ~99% (при Dropout 0.5) | Нестабільна (показник валідації дуже рваний) | Ні (явні ознаки недонавчання при високому dropout) | Дуже швидко досягла майже ідеальної точності. Її продуктивність є потужною, але вкрай нестабільною від епохи до епохи. |
| InceptionV3| ~99-100% (при Dropout 0.2)| Трохи нестабільна | Ні (явні ознаки недонавчання при високому dropout) | Найкраща модель. Її архітектура виявилася найефективнішою, досягнувши найвищої та найстабільнішої точності. |

```txt
TensorFlow version: 2.19.0
Loading models...
- VGG16 model loaded successfully.
- ResNet50 model loaded successfully.
- InceptionV3 model loaded successfully.

========================================
ANALYZING IMAGE: dog.2.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 2s 2s/step
[VGG16       ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 4s 4s/step
[ResNet50    ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 6s 6s/step
[InceptionV3 ] Prediction: DOG  (Raw Score: 1.0000)

========================================
ANALYZING IMAGE: dog.4.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 40ms/step
[VGG16       ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 42ms/step
[ResNet50    ] Prediction: DOG  (Raw Score: 0.9999)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 55ms/step
[InceptionV3 ] Prediction: DOG  (Raw Score: 0.9983)

========================================
ANALYZING IMAGE: cat.4.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 37ms/step
[VGG16       ] Prediction: CAT  (Raw Score: 0.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 40ms/step
[ResNet50    ] Prediction: CAT  (Raw Score: 0.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 46ms/step
[InceptionV3 ] Prediction: CAT  (Raw Score: 0.0000)

========================================
ANALYZING IMAGE: dog.5.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 37ms/step
[VGG16       ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 41ms/step
[ResNet50    ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 46ms/step
[InceptionV3 ] Prediction: DOG  (Raw Score: 1.0000)

========================================
ANALYZING IMAGE: cat.5.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 38ms/step
[VGG16       ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 41ms/step
[ResNet50    ] Prediction: CAT  (Raw Score: 0.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 49ms/step
[InceptionV3 ] Prediction: CAT  (Raw Score: 0.0000)

========================================
ANALYZING IMAGE: dog.1.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 38ms/step
[VGG16       ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 42ms/step
[ResNet50    ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 47ms/step
[InceptionV3 ] Prediction: DOG  (Raw Score: 1.0000)

========================================
ANALYZING IMAGE: cat.1.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 37ms/step
[VGG16       ] Prediction: CAT  (Raw Score: 0.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 40ms/step
[ResNet50    ] Prediction: CAT  (Raw Score: 0.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 46ms/step
[InceptionV3 ] Prediction: CAT  (Raw Score: 0.0001)

========================================
ANALYZING IMAGE: cat.2.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 36ms/step
[VGG16       ] Prediction: CAT  (Raw Score: 0.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 40ms/step
[ResNet50    ] Prediction: CAT  (Raw Score: 0.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 48ms/step
[InceptionV3 ] Prediction: CAT  (Raw Score: 0.0000)

========================================
ANALYZING IMAGE: cat.3.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 69ms/step
[VGG16       ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 56ms/step
[ResNet50    ] Prediction: CAT  (Raw Score: 0.0001)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 74ms/step
[InceptionV3 ] Prediction: CAT  (Raw Score: 0.0001)

========================================
ANALYZING IMAGE: dog.3.png
========================================
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 50ms/step
[VGG16       ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 54ms/step
[ResNet50    ] Prediction: DOG  (Raw Score: 1.0000)
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 64ms/step
[InceptionV3 ] Prediction: DOG  (Raw Score: 1.0000)
```
