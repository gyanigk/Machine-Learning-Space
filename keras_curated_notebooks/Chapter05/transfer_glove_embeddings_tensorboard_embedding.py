from keras.layers.core import Dense, Dropout
from keras.models import Sequential
from keras.preprocessing.sequence import pad_sequences
from keras.utils import np_utils
from sklearn.model_selection import train_test_split
import collections
import nltk
import numpy as np
from make_tensorboard import make_tensorboard
import codecs

np.random.seed(42)

INPUT_FILE = "data/umich-sentiment-train.txt"
GLOVE_MODEL = "data/glove.6B.100d.txt"
VOCAB_SIZE = 5000
EMBED_SIZE = 100
BATCH_SIZE = 64
NUM_EPOCHS = 10

print("reading data...")
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

print("creating vocabulary...")
word2index = collections.defaultdict(int)
for wid, word in enumerate(counter.most_common(VOCAB_SIZE)):
    word2index[word[0]] = wid + 1
vocab_sz = len(word2index) + 1
index2word = {v: k for k, v in word2index.items()}
index2word[0] = "_UNK_"

print("creating word sequences...")
ws, ys = [], []
fin = codecs.open(INPUT_FILE, "r", encoding='utf-8')
for line in fin:
    label, sent = line.strip().split("\t")
    ys.append(int(label))
    words = [x.lower() for x in nltk.word_tokenize(sent)]
    wids = [word2index[word] for word in words]
    ws.append(wids)
fin.close()
W = pad_sequences(ws, maxlen=maxlen)
Y = np_utils.to_categorical(ys)

# load GloVe vectors
print("loading GloVe vectors...")
word2emb = collections.defaultdict(int)
fglove = open(GLOVE_MODEL, "rb")
for line in fglove:
    cols = line.strip().split()
    word = cols[0].decode('utf-8')
    embedding = np.array(cols[1:], dtype="float32")
    word2emb[word] = embedding
fglove.close()

print("transferring embeddings...")
X = np.zeros((W.shape[0], EMBED_SIZE))
for i in range(W.shape[0]):
    E = np.zeros((EMBED_SIZE, maxlen))
    words = [index2word[wid] for wid in W[i].tolist()]
    for j in range(maxlen):
        E[:, j] = word2emb[words[j]]
    X[i, :] = np.sum(E, axis=1)

Xtrain, Xtest, Ytrain, Ytest = \
    train_test_split(X, Y, test_size=0.3, random_state=42)
print(Xtrain.shape, Xtest.shape, Ytrain.shape, Ytest.shape)

model = Sequential()
model.add(Dense(32, input_dim=EMBED_SIZE, activation="relu"))
model.add(Dropout(0.2))
model.add(Dense(2, activation="softmax"))

model.compile(optimizer="adam", loss="categorical_crossentropy",
              metrics=["accuracy"])

tensorboard, log_dir = make_tensorboard(
    set_dir_name='keras_transfer_glove_embeddings',
    embeddings_freq=1,
    embeddings_layer_names='dense_1',
    )
history = model.fit(Xtrain, Ytrain, batch_size=BATCH_SIZE,
                    epochs=NUM_EPOCHS,
                    callbacks=[tensorboard],
                    validation_data=(Xtest, Ytest))

# evaluate model
score = model.evaluate(Xtest, Ytest, verbose=1)
print("Test score: {:.3f}, accuracy: {:.3f}".format(score[0], score[1]))
