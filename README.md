# InvertedIndex v1.0
jiangyunfei93@gmail.com


##读取数据：DATA_path,DICT_path,STOPWORDS_path
  + DATA_path:检索文件放置的文件夹
  + DICT_path:中文字典文件（取自jieba）
  + STOPWORDS_path:停用词表文件

##建立dictionary 和postings：使用字典嵌套字典的方式
  + 预处理：去除标点符号以及’\t’,’\n’
  + 利用正向最大匹配法进行分词
  + 出现停用词则去除，否则加入
###数据储存结构：
  + {key1, key2, key3, … key i},：
  + key=‘words’(单词) -> dictioanay
  + Value  = {key=docID,value=position} -> postings

##输入检索信息：
  + 中文分词
  + 判断单字检索还是多字检索

##检索并计算位置关系：
  + 输入检索信息
  + 使用string.split()分隔空格
###对每一部分进行分词并汇总为words和docs两个lists
  + Words：关键词（排除停用词）
  + Docs：每个关键词对应的postings：
    + {key=docID，value=position}
###对于所有的words对应的postings的key取交集，若存在交集则进行下一步，否则则返回
  + 对于交集中的每一个docID下的位置信息进行合并，得pos List
  + Pos List每个元素前后依次作差：PosList[i+1]-PostList[i]，得到差值表sublist
  + 对于sublist中得元素进行判定，若存在值为1则为Phrase，值小于K则为Proximity Queries结果，否则为同属于同一篇文章
  + #连续的1应该归为连续的句子#

##检索并计算排序权重：
+ 利用Sublist信息，每一个检索得到的doc的权重：
  + Weight = SUM(SubList)/length(subList)，权重值越小则排序越靠前
  + 排序并输出
+ 对于单一word计算权重稍有不同：
  + Weight=length(PosList), 权重值越大则排序越靠前

##打印输出结果:
  + 依照排序权重决定打印顺序
  + 依照位置权重决定结果类型
    + Phrase
    + Proximity within K words


