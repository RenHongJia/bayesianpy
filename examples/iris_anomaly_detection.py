import pandas as pd
import bayesianpy
from bayesianpy.network import Builder as builder

import logging
import os

import matplotlib.pyplot as plt

# Demonstrates one-class classification/ unsupervised clustering to identify the likelihood that a sample has been
# generated by the particular model. Useful for building a model of normality and automatically identifying abnormal
# data.

def main():

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    bayesianpy.jni.attach(logger)

    db_folder = bayesianpy.utils.get_path_to_parent_dir(__file__)
    iris = pd.read_csv(os.path.join(db_folder, "data/iris.csv"), index_col=False)

    # manually build the network, leaving out the 'iris-class' variable
    network = bayesianpy.network.create_network()
    cluster = builder.create_cluster_variable(network, 4)
    node = builder.create_multivariate_continuous_node(network, iris.columns.tolist(), "joint")
    builder.create_link(network, cluster, node)

    with bayesianpy.data.DataSet(iris.drop('iris_class', axis=1), db_folder, logger) as dataset:

        # build the 'normal' model on two of the classes
        model = bayesianpy.model.NetworkModel(network,
                                              logger)


        subset = dataset.subset(iris[(iris.iris_class == "Iris-versicolor") | (iris.iris_class == "Iris-virginica")].index.tolist())

        model.train(subset)

        variables = ['sepal_length','sepal_width','petal_length','petal_width']

        # query the trained model on all the data, including the Iris-setosa class

        # get the loglikelihood value for the whole model on each individual sample,
        # the lower the loglikelihood value the less likely the data point has been
        # generated by the model.
        results = model.batch_query(dataset, [bayesianpy.model.QueryModelStatistics()])
        cmap = plt.cm.get_cmap('Blues_r')
        fig = plt.figure(figsize=(10, 10))
        k = 1
        for i, v in enumerate(variables):
            for j in range(i+1, len(variables)):
                v1 = variables[j]
                ax = fig.add_subplot(3,2,k)
                ax.set_title("{} vs {}".format(v, v1))
                h = ax.scatter(x=iris[v].tolist(), y=iris[v1].tolist(), c=results['loglikelihood'].tolist(),
                        vmin=results.loglikelihood.min(), vmax=results.loglikelihood.max(), cmap=cmap
                        )
                k+=1

        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
        fig.colorbar(h, cax=cbar_ax)
        plt.show()


if __name__ == "__main__":
    main()