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

	Run the clustering.py file which has configurations for WCA using UEMNM for k=4,9,15 and for Limbo using IL for k=4,9,15 and for ACDC
	This creates the output folders - ouput_wca_4, output_wca_9, output_wca_15, output_limbo_4, output_limbo_9, output_limbo_15, acdc

Step 6 - Analyze the clusters created by each algorithm and find the results
		
	Run the analyze_cluster.py file and parse the results stored in cluster_results.txt

Week 2

Step 1 - Run the arcade tools a2a and cvg to calculate the relevant metrics (similarity and distance)
	
	Run the metrics.py file which calculates the a2a and cvg scores betweeen WCA(k=4,9,15) and Limbo(k=4,9,15), between WCA(k=4) and ACDC, between Limbo(k=4) and ACDC
	The results are then stored in metrics_results.txt

Step 2 - LLM Prompting (lightweight model)