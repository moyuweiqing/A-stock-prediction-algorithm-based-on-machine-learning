# A-stock-prediction-algorithm-based-on-machine-learning
**（陆续更新）重新整理过的基于机器学习的股票价格预测算法，里面包含了基本的回测系统以及各种不同的机器学习算法的股票价格预测，包含：LSTM算法、Prophet算法、AutoARIMA、朴素贝叶斯、SVM等**

### 3-11
**回测.py**
提供了一个基本的回测demo，实现股票基本的买入卖出，考虑佣金和印花税

**传统技术面分析算法/Moving_Average.py**
移动平均算法，通过移动窗口的方式进行股票预测，传入窗口长度参数可以进行预测，支持tushare接口直接获取数据并即时进行预测

**传统技术面分析算法/Relative_strength_index.py**
相对强度指数，返回计算期内的相对强度指数计算情况

### 2020-3-10
创建项目，README文件
