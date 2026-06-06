Week 1

Step 1 - Clone the apache tika repository
	
	git clone https://github.com/apache/tika.git

Step 2 - Create the jar for the tika-core directory

	mvn -DskipTests package -pl tika-annotation-processor,tika-core

Step 3 - Use the arcade JavaParser on the created jar to generate the .rsf and .fv files

	java -jar ../arcade_tools/arcade_core_JavaParser.jar tika/tika-core/target/tika-core-4.0.0-SNAPSHOT.jar ../tika-core.rsf ../tika-core.fv "org.apache.tika"
	
Step 4 - Filter the .rsf file to find dependencies for detect and parser
	
	Run the filtering.py file on the tika-core.rsf file and generate the filtered_rsf.rsf file
	
	The initial tika-core.rsf file had 1227 dependencies. After filtering, filtered_rsf.rsf file has 551 dependencies.
	
Step 5 - Use the arcade Clusturer and arcade ACDC to run WCA and Limbo clustering algorithms

	Run the clustering.py file will run the 3 clustering algorithms (WCA, Limbo, ACDC) with WCA and Limbo running for number of clusters from 2 to 50
	The results are stores in the directories - output_wca/, output_limbo/, output_acdc/

Step 6 - Analyze the clusters created by each algorithm and find the results
		
	Run the analyze_cluster.py file and parse the results stored in cluster_details/
	The clustering_summary.csv files contains results for all the clusters generated

Week 2

Step 1 - Run the arcade tools a2a and cvg to calculate the relevant metrics (similarity and distance)
	
	Run the metrics.py file which calculates the a2a and cvg scores betweeen all the three algorithms
	The results are then stored in metrics_summary.csv

Step 2 - LLM Prompting (lightweight model)

	Use the google collab sheet - https://colab.research.google.com/drive/1kefRfgNJNmbpsQKID02KcVyM293I4m3M?usp=sharing
	To load in the LLM model, perform quantization to reduce the model size and precision, the tokenizer configuration is set up for communicating with the LLM.
	We can finetune the prompt as well as the hyperparameters for the model (temp, top_p, max_tokens and do_sample) to determine what works best

Week 3

Step 1 - Running semantic clustering

	Use the google collab sheet - https://colab.research.google.com/drive/1wlyR-CUhVUHHYLvohTfZ4zj2j6Nw6QF6?usp=sharing
	First upload the "tika_data.zip" folder to colab
	We use quantization to reduce memory requirements, then load in the embeddings model
	The source code is analysed using this model, and the script runs to create the different required matrices
	Once the script has finished running, the created cluster files will be downloaded to your system.
	Unzip the output_arc folder and copy it to the same directory as this repository

Step 2 - Calculating metrics to compare the semantic and structural clustering methods

	Run the python script metrics_week3.py to calculate the a2a and cvg scores between the 4 algorithms for various k-values and alpha-values
	The results are stored in metrics_week3_summary.csv file
	Analyze the results to determine the best parameters for getting good clusters


Week 4 - LLM based architecture tasks

Step 1 - Running LLM based architectural summary 
	
	Use the google collab sheet - https://colab.research.google.com/drive/1LfqAIo0jm3KDlumgZ0JRDtkSr6jJQP8Y?usp=sharing
	First upload the tika-core.zip folder from the apache tika repository to colab 
	Also upload the arc cluster file which you want to analyse
	Make sure the source files and rsf path variable match according to the files you have uploaded
	Start the script
	Once the script has finished running, the generated LLM summaries will be downloaded to your system
	Unzip the "week4_summary_***.zip" folder and analyze the results
