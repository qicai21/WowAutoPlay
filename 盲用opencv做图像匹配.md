# 盲用opencv做图像匹配

## opencv的算法和版本

opencv使用了许多算法，简单说几个其中涉及匹配时比较重要的：

- ORB：基于FAST关键点检测和BRIEF的描述符技术相结合
- SURF：Opencv的SURF类是Hessian算法和SURF算法组合
- DoG：DoG是对同一图像使用不同高斯滤波器所得的结果
- SIFT: SIFT是通过一个特征向量来描述关键点周围区域的情况，Opencv的SIFT类是DoG和SIFT算法组合。

收SURF和SIFT的开源条款变更的限制，opencv的版本目前需要维持在3.4，而不能使用4.+。

## 我们的目标

之所以是说盲用，就是在不去学习opencv的整体架构和系统知识的前提下，通过对网上样例的拼接，实现我们要匹配的目的。

了解到的基本知识：

**图像匹配**：cv2.matchTemplate()不能满足我们的需求，因为template图片被拉伸了，甚至有时会被旋转，尺寸不一样， 识别就不可能。具体原因可见[Opencv 第21集 目标模版匹配](https://www.bilibili.com/video/BV1tx411C7BN?from=search&seid=16241129926615649013)中关于matchTemplate的匹配原理展示。

**那么我们就需要进行目标特征识别：**

## BFMatching