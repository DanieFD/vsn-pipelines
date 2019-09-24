//
// Version: 0.1.0
// Test: passed
// Command: 
//  nextflow run src/singlecelltxbenchmark/pipelines/bec__bbknn -profile singularity --tenx_folder data/01.count/**/filtered_feature_bc_matrix --project_name tiny
//
/*
 */ 
import static groovy.json.JsonOutput.*

nextflow.preview.dsl=2

include groupParams from '../../utils/utils.nf'

//////////////////////////////////////////////////////
//  Define the parameters for current testing proces
PARAMS_GROUPED = groupParams( params )

println(prettyPrint(toJson(PARAMS_GROUPED)))

include SC__CELLRANGER__MKFASTQ from '../../processes/cellranger/mkfastq' params(PARAMS_GROUPED['SC__CELLRANGER__MKFASTQ'])
include SC__CELLRANGER__COUNT from '../../processes/cellranger/count' params(PARAMS_GROUPED['SC__CELLRANGER__COUNT'])

//////////////////////////////////////////////////////
//  Define the workflow 

/*
 * Run the workflow for each 10xGenomics CellRanger output folders specified.
 */ 
workflow {
    main:
        SC__CELLRANGER__MKFASTQ(file(params.sc.cellranger.mkfastq.samplesheet), file(params.sc.cellranger.mkfastq.runFolder))
        SC__CELLRANGER__COUNT(file(params.sc.cellranger.count.transcriptome), SC__CELLRANGER__MKFASTQ.out.flatten())
}
