#!/bin/bash

# Set strict mode
set -euo pipefail

# Configuration
readonly JAVA_MEMORY="16G"
readonly SPLITTER_MAX_NODES=1200000
readonly LOG_FILE="map_creation.log"
#Java options to be used to be more verbose
# readonly JAVA_OPTS="-Xmx${JAVA_MEMORY} -ea -Dlog.config=../logging.properties"
readonly JAVA_OPTS="-Xmx${JAVA_MEMORY}"

# Color codes for pretty output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Initialize timing
start_time=$(date +%s)
current_date=$(date "+%d.%m.%Y")

# Logging functions
log() {
    local level=$1
    shift
    local message=$*
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() {
    log "INFO" "${BLUE}$*${NC}"
}

warn() {
    log "WARN" "${YELLOW}$*${NC}"
}

error() {
    log "ERROR" "${RED}$*${NC}"
    exit 1
}

success() {
    log "SUCCESS" "${GREEN}$*${NC}"
}

# Display banner
display_banner() {
    local message=$1
    local banner_width=70
    local padding=$(( (banner_width - ${#message}) / 2 ))
    
    echo -e "\n${BLUE}#$(printf '%.0s#' {1..68})#${NC}"
    echo -e "${BLUE}#$(printf '%.0s ' $(seq 1 $padding))${message}$(printf '%.0s ' $(seq 1 $padding))#${NC}"
    echo -e "${BLUE}#$(printf '%.0s#' {1..68})#${NC}\n"
}

# Calculate elapsed time
calculate_elapsed_time() {
    local elapsed_time=$(( $(date +%s) - start_time ))
    local days=$(( elapsed_time / 86400 ))
    local hours=$(( (elapsed_time % 86400) / 3600 ))
    local minutes=$(( (elapsed_time % 3600) / 60 ))
    local seconds=$(( elapsed_time % 60 ))
    
    local result=""
    [[ $days -gt 0 ]] && result+="${days}d "
    [[ $hours -gt 0 ]] && result+="${hours}h "
    [[ $minutes -gt 0 ]] && result+="${minutes}m "
    result+="${seconds}s"
    
    echo "$result"
}

# Check prerequisites
check_prerequisites() {
    local required_commands=("java" "makensis" "sed")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command '$cmd' not found. Please install it first."
        fi
    done
}

# Process contour files
process_contour_files() {
    local poly=$1
    local mapname_courbes=$2
    
    for file_courbe in *.osm.gz; do
		local img_count=$(find . -maxdepth 1 -name "*.img" -type f | wc -l)
        local index=$(printf '%04d' "$img_count")
        info "Processing contour file: $file_courbe (index: $index)"
        
        # Split contour file
        java $JAVA_OPTS -jar ../splitter/splitter.jar \
            --mapid="${mapname_courbes}${index}" \
            --max-nodes="$SPLITTER_MAX_NODES" \
            --polygon-file="$poly" \
            --keep-complete=false "$file_courbe" || {
                warn "First split attempt failed, retrying without polygon file..."
                java $JAVA_OPTS -jar ../splitter/splitter.jar \
                    --mapid="${mapname_courbes}${index}" \
                    --max-nodes="$SPLITTER_MAX_NODES" \
                    --keep-complete=false "$file_courbe"
            }
        
        mv template.args courbes.args
        
        # Create contour maps
        info "Creating contour map for index $index"
        java $JAVA_OPTS -jar ../mkgmap/mkgmap.jar \
            --verbose -c ../options_courbes.args -c courbes.args
	    
		# Cleanup
		rm -f ${mapname_courbes}*.osm.pbf areas.list areas.poly courbes.args densities-out.txt osmmap.img osmmap.tdb rm none-areas.poly none-template.args
        
    done
}

# Main map creation
create_main_map() {
    local file=$1
    local mapname=$2
    local type=$3
    local land=$4
    
    info "Creating main map"
    if [[ ! -f "${mapname}.osm.pbf" ]]; then
        info "Splitting main OSM file..."
        java $JAVA_OPTS -jar ../splitter/splitter.jar \
            --mapid="${mapname}000" \
            --max-nodes="$SPLITTER_MAX_NODES" \
            --keep-complete=true \
            --route-rel-values=foot,hiking,bicycle \
            --overlap=0 "$file"
        mv template.args map.args
    fi
    
    info "Compiling Garmin image..."
    java $JAVA_OPTS -jar ../mkgmap/mkgmap.jar -c "../options_${type}.args" -c map.args
        
    local description="MapUtagawa (Map${type^} ${land} ${current_date})"
    local family_name="MapUtagawa ${land}"
    local series_name="MapUtagawa ${land} ${current_date}"
    
    if [[ -f "${mapname_courbes}0000.img" ]]; then
        info "Merging contours with main map..."
        java $JAVA_OPTS -jar ../mkgmap/mkgmap.jar \
            --mapname="${mapname}000" \
            --family-id="$mapname" \
            --family-name="$family_name" \
            --series-name="$series_name" \
            --description="$description" \
            -c "../options_${type}.args" \
			--gmapsupp \
            "../style/${type}.typ" \
            ${mapname}*.img ${mapname_courbes}*.img
    else
        info "Creating map without contours..."
        java $JAVA_OPTS -jar ../mkgmap/mkgmap.jar \
            --mapname="${mapname}000" \
            --family-id="$mapname" \
            --family-name="$family_name" \
            --series-name="$series_name" \
            --description="$description" \
            -c "../options_${type}.args" \
            --gmapsupp \
			"../style/${type}.typ" \
            ${mapname}*.img
    fi
}

# Main execution
main() {
    # Validate arguments
    if [[ $# -ne 3 ]]; then
        error "Usage: $0 <land> <id> <type>"
    fi
    
    local land="$1"
    local id="$2"
    local type="$3"
    
    # Initialize log file
	rm "$LOG_FILE"
    : > "$LOG_FILE"
    
    # Check prerequisites
    check_prerequisites
    
    # Display start banner
    display_banner "Starting map creation for $land (ID: $id)"
    
    # Prepare variables
    local land_lower=$(echo "$land" | tr '[:upper:]' '[:lower:]' | tr ' ' _)
    local land_without_space=$(echo "$land" | tr ' ' _)
    local file="${land_lower}.osm.pbf"
    local poly="${land_lower}.poly"
    local type_upper="$(tr '[:lower:]' '[:upper:]' <<< "${type:0:1}")${type:1}"
    local mapname="45$id"
    local mapname_courbes="9$id"
    local name_file="Map${type_upper}_${land_without_space}_"
    
    # Change to working directory
    cd "carte_$land_lower" || error "Failed to change to working directory"
    
    # Process contour files if they exist
	local osm_count=$(find . -maxdepth 1 -name "*.osm.gz" -type f | wc -l)
    # local osm_count=$(ls -1 *.osm.gz 2>/dev/null | wc -l || echo "0")
    if (( osm_count > 0 )); then
        info "Found $osm_count contour files to process"
        rm -f *.img
        process_contour_files "$poly" "$mapname_courbes"
        rm -f *.osm.gz
        success "Contour processing complete"
    fi
    
    # Create main map
    create_main_map "$file" "$mapname" "$type" "$land"
    
    # Create installer
    # info "Creating installer..."
    # cp "../style/${type}.typ" "./${type}.typ"
    # sed -i 's_SetCompressor /SOLID lzma_SetCompressor /SOLID zlib_g' ./osmmap.nsi
    # makensis -V4 ./osmmap.nsi
    
    # Cleanup and organize output
    info "Organizing output files..."
    local output_dir="/var/data/garminmaps/UtagawaVTTmap/${land_without_space}"
    mkdir -p "$output_dir"
    
    # Move final files to output directory
    if [[ -f "gmapsupp.img" ]]; then
		mv -f "gmapsupp.img" "${output_dir}/${name_file}latest.img"
	fi
	
    # mv -f "MapUtagawa ${land}.exe" "${output_dir}/MapUtagawa_${land_without_space}_${current_date}.exe"
    
    # Cleanup temporary files
    info "Cleaning up temporary files..."
    rm -f ${mapname}*.img ${mapname}*.osm.pbf areas.list areas.poly map.args \
        densities-out.txt osmmap.img osmmap.tdb osmmap.nsi x${type}.typ ${type}.typ \
		osmmap_mdr.img osmmap.mdx osmmap_license.txt
	rm -f courbes.args none-areas.poly none-template.args
	
	trap 'rm -f *.tmp' EXIT
        
    # Display completion banner and timing
    success "Map creation completed in $(calculate_elapsed_time)"
    
    cd ..
}

# Execute main function with error handling
{
    main "$@"
} 2> >(while read -r line; do error "$line"; done)