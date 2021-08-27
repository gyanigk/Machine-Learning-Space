from gensim.models import KeyedVectors
from keras.layers.core import Dense, SpatialDropout1D
from keras.layers.convolutional import Conv1D
from keras.layers.embeddings import Embedding
from keras.layers.pooling import GlobalMaxPooling1D
from keras.models import Sequential
from keras.preprocessing.sequence import pad_sequences
from keras.utils import np_utils
from sklearn.model_selection import train_test_split
import collections
from make_tensorboard import make_tensorboard
import nltk
import numpy as np
import os
import codecs

np.random.seed(42)

INPUT_FILE = "data/umich-sentiment-train.txt"
# You have to get the model
#    https://drive.google.com/uc?id=0B7XkCwpI5KDYNlNUTTlSS21pQmM&export=download
WORD2VEC_MODEL = "data/GoogleNews-vectors-negative300.bin.gz"
VOCAB_SIZE = 5000
EMBED_SIZE = 300
NUM_FILTERS = 256
NUM_WORDS = 3
BATCH_SIZE = 64
NUM_EPOCHS = 20

counter = collections.Counter()
fin = codecs.open(INPUT_FILE, "r", encoding='utf-8')
maxlen = 0
for line in fin:
    _, sent = line.strip().split("\t")
    words = [x.lower() for x in nltk.word_tokenize(sent)]
    if len(words) > maxlen:
        maxlen = len(words)
    for word in words:
        counter[word] += 1
fin.close()

word2index = collections.defaultdict(int)
for wid, word in enumerate(counter.most_common(VOCAB_SIZE)):
    word2index[word[0]] = wid + 1
vocab_sz = len(word2index) + 1
index2word = {v: k for k, v in word2index.items()}

xs, ys = [], []
fin = codecs.open(INPUT_FILE, "r", encoding='utf-8')
for line in fin:
    label, sent = line.strip().split("\t")
    ys.append(int(label))
    words = [x.lower() for x in nltk.word_tokenize(sent)]
    wids = [word2index[word] for word in words]
    xs.append(wids)
fin.close()
X = pad_sequences(xs, maxlen=maxlen)
Y = np_utils.to_categorical(ys)

Xtrain, Xtest, Ytrain, Ytest = \
    train_test_split(X, Y, test_size=0.3, random_state=42)
print(Xtrain.shape, Xtest.shape, Ytrain.shape, Ytest.shape)

# load word2vec model
word2vec = KeyedVectors.load_word2vec_format(WORD2VEC_MODEL, binary=True)
embedding_weights = np.zeros((vocab_sz, EMBED_SIZE))
for word, index in word2index.items():
    try:
        embedding_weights[index, :] = word2vec[word]
    except KeyError:
        pass

model = Sequential()
model.add(Embedding(vocab_sz, EMBED_SIZE, input_length=maxlen,
                    weights=[embedding_weights],
                    trainable=True))
model.add(SpatialDropout1D(0.2))
model.add(Conv1D(filters=NUM_FILTERS, kernel_size=NUM_WORDS,
                 activation="relu"))
model.add(GlobalMaxPooling1D())
model.add(Dense(2, activation="softmax"))

model.compile(optimizer="adam", loss="categorical_crossentropy",
              metrics=["accuracy"])
tensorboard, log_dir = make_tensorboard(
    set_dir_name='keras_finetune_word2vec_embeddings',
    embeddings_freq=1,
    embeddings_metadata='embedding/metadata.tsv'
    )

history = model.fit(Xtrain, Ytrain, batch_size=BATCH_SIZE,
                    epochs=NUM_EPOCHS,
                    callbacks=[tensorboard],
                    validation_data=(Xtest, Ytest))

# evaluate model
score = model.evaluate(Xtest, Ytest, verbose=1)
print("Test score: {:.3f}, accuracy: {:.3f}".format(score[0], score[1]))

word_list = []
for wid, word in enumerate(counter.most_common(VOCAB_SIZE)):
    word_list.append(word[0])
log_dir = log_dir + "/embedding/"
if os.path.exists(log_dir) is not True:
    os.mkdir(log_dir)
meta_data_file = log_dir + 'metadata.tsv'
with open(meta_data_file, 'w', encoding='utf8') as f:
    for name in word_list:
        f.write('%s\n' % str(name))
    f.write('__UNK__\n')
