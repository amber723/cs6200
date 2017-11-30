import pickle
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans

DATA_PATH = '/Users/xinshu/desktop/CS6200/Assignments/HW8/data/'

def build_matrix():
    all_matrix = pickle.load(open(DATA_PATH + 'feature_matrix.pkl'))
    used_ids = pickle.load(open(DATA_PATH + 'all_ids.pkl'))
    data_list = []

    for doc in used_ids:
        data_list.append(all_matrix[doc])

    return data_list, used_ids

if __name__ == "__main__":
    data_samples, ids = build_matrix()

    print "Finished fetching data"

    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=3,
                                       stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(data_samples)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()

    lda = LatentDirichletAllocation(n_topics=200, learning_method='online',
                                    learning_offset=50, random_state=0)
    lda.fit(tfidf)
    topic_list = lda.transform(tfidf)

    print "Lda finished"

    km = KMeans(n_clusters=25, init='k-means++', max_iter=300, n_init=1)
    km.fit(topic_list)
    result = km.predict(topic_list)

    of = open(DATA_PATH + 'clustering.txt', "w")
    for i in xrange(len(result)):
        of.write(ids[i] + " " + str(result[i]) + " " +
                 str(topic_list[i].argsort()[-1:][::-1][0]) + "\n")
