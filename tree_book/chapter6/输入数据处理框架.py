import tensorflow as tf 

#创建文件列表，并通过文件列表创建输入文件队列。在调用输入数据处理流程前，需要
#统一所有原始数据的格式并将它们存储到TFRecoed文件中
files = tf.train.match_filenames_once("./path/to/data.tfrecords-*")
filename_queue =tf.train.string_input_producer(files,shuffle=False)

#计息TFRecoed文件中的数据，这里假设image存储的是图像的原始数据，label为标签
#height，width和channels
reader = tf.TFRecordReader()
_,serialized_example = reader.read(filename_queue)
features = tf.parse_single_example(
    serialized_example,
    features = 
    {
        'image': tf.FixedLenFeature([],tf.string),
        'label': tf.FixedLenFeature([],tf.int64),
        'height': tf.FixedLenFeature([].tf.int64),
        'width': tf.FixedLenFeature([],tf.int64),
        'channels': tf.FixedLenFeature([],tf.int64),
    }
)
image,label = features['image'],features['label']
height,width = features['height'],features['width']
channels = features['channels']

#从原始图像数据解析出像素矩阵，并根据图像尺寸还原图像
decoded_image = tf.decode_raw(image,tf.uint8)
decoded_image.set_shape([height,width,channels])
#定义神经网络输入层图片的大小
image_size=299
#图像预处理
distorted_image = prepocess_for_train(
    decoded_image,image_size,image_size,None
)

#将处理后的图像和标签数据通过tf.train.shuffle_batch整理成神经网络训练时
#需要的batch
min_after_dequeue = 10000
batch_size = 100
capacity = min_after_dequeue + 3*batch_size
image_batch, label_batch = tf.train.shuffle_batch(
    [distorted_image,label],batch_size=batch_size,capacity=capacity,min_after_dequeue=min_after_dequeue
)
#定义神经网络结构以及优化过程，image_batch可以作为输入提供给神经网络的输入层
#label_batch则提供了输入batch中样例的正确答案
logit = inference(image_batch)
loss = calc_loss(logit,label_batch)
train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)

#声明绘画并运行神经网络的优化过程
with tf.Session() as sess:
    tf.global_variables_initializer().run()
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess,coord=coord)

    #神经网络训练过程
    for i in range(TRAINING_ROUDNS):
        sess.run(train_step)

    #停止所有线程
    coord.request_stop()
    coord.join()

