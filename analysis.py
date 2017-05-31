import warnings
import numpy as np
from sklearn.cross_validation import KFold, cross_val_score
from sklearn.ensemble import GradientBoostingClassifier 
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.cluster import SpectralClustering
from sklearn.metrics import roc_auc_score


def PrepareData():
    data_file = open('pupil.csv', 'r')
    data = [list(map(float, x.split(';'))) 
    for x in data_file.read().split('\n') if x]
    data_file.close()
    X = [x[:-1] for x in data]
    Y = [int(x[-1]) for x in data]
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    return X, Y

def LogRegL2(X, Y):
    quality = 0
    c_r = -1
    for c in [0.001, 0.01, 0.1, 1, 10, 100, 1000]:
        kf = KFold(n=len(Y), shuffle=True, n_folds=5)
        clf = LogisticRegression(penalty='l2', C=c)
        quality_t = (sum(cross_val_score(
        clf, X, y=Y, scoring='roc_auc', cv=kf)) / 5)
        if quality_t > quality:
            quality = quality_t
            c_r = c
    print(' Качество логистической регрессии с l2 регуляризацией:', quality,
    'при значении с', c_r)
    
def LogRegL1W(X, Y):
    c = 1
    clf = LogisticRegression(penalty='l1', C=c)
    clf.fit(X, Y)
    weights = clf.coef_[0]
    print('Веса признаков в логистической регрессии с l1 регуляризацией:')
    print(
        ' Среднее положение по оси X', weights[0], '\n',
        'Выборочная дисперсия по оси X', weights[1], '\n',
        'Среднее положение по оси Y', weights[2], '\n',
        'Выборочная дисперсия по оси Y', weights[3], '\n',
        'Средний диаметр', weights[4], '\n',
        'Выборочная дисперсия диаметра', weights[5], '\n',
        'Средняя скорость перемещения зрачка', weights[6], '\n',
    )
    
def LogRegL1(X, Y):
    quality = 0
    c_r = -1
    for c in [0.001, 0.01, 0.1, 1, 10, 100, 1000]:
        kf = KFold(n=len(Y), shuffle=True, n_folds=5)
        clf = LogisticRegression(penalty='l1', C=c)
        quality_t = (sum(cross_val_score(
        clf, X, y=Y, scoring='roc_auc', cv=kf)) / 5)
        if quality_t > quality:
            quality = quality_t
            c_r = c
    print(' Качество логистической регрессии с l1 регуляризацией:', quality,
    'при значении с', c_r)
    
def GB(X, Y):
    n = 100
    kf = KFold(n=len(Y), shuffle=True, n_folds=5)
    clf = GradientBoostingClassifier(n_estimators=n)
    quality = sum(cross_val_score(clf, X, y=Y, scoring='roc_auc', cv=kf)) / 5
    print(' Качество градиентного бустинга:', quality)
    
def SGD(X, Y):
    kf = KFold(n=len(Y), shuffle=True, n_folds=5)
    clf = SGDClassifier()
    quality = sum(cross_val_score(clf, X, y=Y, scoring='roc_auc', cv=kf)) / 5
    print(' Качество стохастического градиента:', quality)
    
def SVCM(X, Y):
    c = 1
    kf = KFold(n=len(Y), shuffle=True, n_folds=5)
    clf = SVC(C = c)
    quality = sum(cross_val_score(clf, X, y=Y, scoring='roc_auc', cv=kf)) / 5
    print(' Качество метода опорных векторов:', quality)
    
def NB(X, Y):
    kf = KFold(n=len(Y), shuffle=True, n_folds=5)
    clf = GaussianNB()
    quality = sum(cross_val_score(clf, X, y=Y, scoring='roc_auc', cv=kf)) / 5
    print(' Качество наивного байеса:', quality)
    
def RF(X, Y):
    n = 100
    kf = KFold(n=len(Y), shuffle=True, n_folds=5)
    clf = RandomForestClassifier(n_estimators=n)
    quality = sum(cross_val_score(clf, X, y=Y, scoring='roc_auc', cv=kf)) / 5
    print(' Качество рандомного леса:', quality)
    
def NN(X, Y):
    kf = KFold(n=len(Y), shuffle=True, n_folds=5)
    clf = MLPClassifier()
    quality = sum(cross_val_score(clf, X, y=Y, scoring='roc_auc', cv=kf)) / 5
    print(' Качество нейронной сети:', quality)
    
def KMC(X, Y):
    clf = KMeans(n_clusters=2)
    Yp = clf.fit_predict(X)
    print(' Качество метода к ближайших соседей:', roc_auc_score(Yp, Y))
    
def AC(X, Y):
    clf = AgglomerativeClustering(n_clusters=2)
    Yp = clf.fit_predict(X)
    print(' Качество агломеративной кластеризации:', roc_auc_score(Yp, Y))
    
def SC(X, Y):
    clf = SpectralClustering(n_clusters=2)
    Yp = clf.fit_predict(X)
    print(' Качество спектральной кластеризации:', roc_auc_score(Yp, Y))
    
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    X, Y = PrepareData()
    print('Показатели различных моделей классификации:')
    LogRegL2(X, Y)
    LogRegL1(X, Y)
    GB(X, Y)
    RF(X, Y)
    NN(X, Y)
    NB(X, Y)
    SGD(X, Y)
    SVCM(X, Y)
    
    LogRegL1W(X, Y)
    
    print('Показатели различных моделей кластеризации:')
    KMC(X,Y)
    AC(X,Y)
    SC(X,Y)
