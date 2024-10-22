"""

"""
from tqdm import tqdm
# from tensorflow.keras.layers import Embedding, Bidirectional, LSTM, Dense
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.optimizers import Adam

import numpy as np


class NerDatasetReader:
    def read(self, data_path):
        data_parts = ['train', 'valid', 'test']
        extension = '.txt'
        dataset = {}
        for data_part in tqdm(data_parts):
            file_path = data_path + data_part + extension
            dataset[data_part] = self.read_file(str(file_path))
        return dataset
            
    def read_file(self, file_path):
        fileobj = open(file_path, 'r', encoding='utf-8')
        samples = []
        tokens = []
        tags = []

        for content in fileobj:
            content = content.strip('\n')
            if content == '-DOCSTART- -X- -X- O':
                pass
            elif content == '':
                if len(tokens) != 0:
                    # 每一句保存为了两个list，一个是单词list，另一个是标注list
                    samples.append((tokens, tags))
                    tokens = []
                    tags = []
            else:
                contents = content.split(' ')
                tokens.append(contents[0])
                tags.append(contents[-1])
        return samples


def get_dicts(datas):
    w_all_dict, n_all_dict = {}, {}
    for sample in datas:
        for token, tag in zip(*sample):
            if token not in w_all_dict.keys():
                w_all_dict[token] = 1
            else:
                w_all_dict[token] += 1
            
            if tag not in n_all_dict.keys():
                n_all_dict[tag] = 1
            else:
                n_all_dict[tag] += 1

    sort_w_list = sorted(w_all_dict.items(),  key=lambda d: d[1], reverse=True)
    sort_n_list = sorted(n_all_dict.items(),  key=lambda d: d[1], reverse=True)
    # 保留前15999个常用的单词，新增了一个"UNK"代表未知单词。
    w_keys = [x for x, _ in sort_w_list[:15999]]
    w_keys.insert(0, "UNK")

    n_keys = [x for x, _ in sort_n_list]
    w_dict = {x:i for i, x in enumerate(w_keys)}
    n_dict = {x:i for i, x in enumerate(n_keys)}
    return(w_dict, n_dict)


def w2num(datas, w_dict, n_dict):
    ret_datas = []
    for sample in datas:
        num_w_list, num_n_list = [], []
        for token, tag in zip(*sample):
            if token not in w_dict.keys():
                token = "UNK"
            if tag not in n_dict:
                tag = "O"
            num_w_list.append(w_dict[token])
            num_n_list.append(n_dict[tag])
        ret_datas.append((num_w_list, num_n_list, len(num_n_list)))
    return(ret_datas)


def len_norm(data_num, lens=80):
    ret_datas = []
    for sample1 in list(data_num):
        sample = list(sample1)
        ls = sample[-1]
        # print(sample)
        while(ls < lens):
            sample[0].append(0)
            ls = len(sample[0])
            sample[1].append(0)
        else:
            sample[0] = sample[0][:lens]
            sample[1] = sample[1][:lens]
        ret_datas.append(sample[:2])
    return(ret_datas)


def build_model(num_classes=9):
    model = Sequential()
    model.add(Embedding(16000, 256, input_length=80))
    model.add(Bidirectional(LSTM(128,return_sequences=True),merge_mode="concat"))
    model.add(Bidirectional(LSTM(128,return_sequences=True),merge_mode="concat"))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(num_classes, activation='softmax'))
    return(model)


Train = True

if __name__ == "__main__":
    ds_rd = NerDatasetReader()
    dataset = ds_rd.read("./data/ner/conll2003_v2/")
    # print(dataset["test"])
    w_dict, n_dict = get_dicts(dataset["train"])
    # print(w_dict)
    # print(n_dict)
    data_num = {}
    # ([token对应的词典索引数字...], [标签对应的索引数字...], [句子tokens长度])
    data_num["train"] = w2num(dataset["train"], w_dict, n_dict)
    # print(data_num["train"][:10])
    # 我们输出句子长度的统计，发现最大值113，最小值为1，为了方便统一训练，我们归一化长度为80
    w_lens = [data[-1] for data in data_num["train"]]
    # print(max(w_lens), min(w_lens))
    # 句子长度归一化操作，这里采用padding为0，就是当做“UNK”与“O”来用，其实也可以使用Mask方法等
    data_norm = {}
    data_norm["train"] = len_norm(data_num["train"])
    print(data_norm["train"][:10])
    # 
    # model = build_model()
    # print(model.summary())
    # opt = Adam(0.001)
    # model.compile(loss="sparse_categorical_crossentropy",optimizer=opt)

    # train_data = np.array(data_norm["train"])
    # train_x = train_data[:,0,:]
    # train_y = train_data[:,1,:]


    # if(Train):
    #     print(train_x.shape)
    #     model.fit(x=train_x,y=train_y,epochs=10,batch_size=200,verbose=1,validation_split=0.1)
    #     model.save("model.h5")
    # else:
    #     model.load_weights("model.h5")
    #     pre_y = model.predict(train_x[:4])

    #     print(pre_y.shape)

    #     pre_y = np.argmax(pre_y,axis=-1)

    #     for i in range(0,len(train_y[0:4])):
    #         print("label "+str(i),train_y[i])
    #         print("pred "+str(i),pre_y[i])