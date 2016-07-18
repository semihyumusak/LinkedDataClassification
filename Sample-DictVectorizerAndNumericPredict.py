measurements = [
    {'city': '1', 'temperature': 33},
    {'city': '1', 'temperature': 12},
    {'city': '1', 'temperature': 18},
    {'city': '1', 'temperature': 13},
    {'city': '1', 'temperature': 19},
    {'city': '1', 'temperature': 33},
]

measurements2 = [
    {'city': '1', 'temperature': 8},
    {'city': '1', 'temperature': 11},
    {'city': '1', 'temperature': 17},
    {'city': '1', 'temperature': 12},
    {'city': '1', 'temperature': 18},
    {'city': '1', 'temperature': 32},
]
y = ['hot','cold','warm','cold','warm','hot']
from sklearn.feature_extraction import DictVectorizer
vec = DictVectorizer()

arr = vec.fit_transform(measurements).toarray()
arr2 = vec.fit_transform(measurements2).toarray()

feats = vec.get_feature_names()


from sklearn.svm import SVC
clf = SVC(kernel="linear", C=0.025)
clf.fit(arr, y)
predict = clf.predict(arr2)

print("finished")