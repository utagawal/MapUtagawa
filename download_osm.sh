#!/bin/bash

# Configuration
set -e  # Arrête le script si une commande échoue
TIMEOUT=600  # Timeout en secondes pour curl

# Fonction de logging
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] ${level}: ${message}"
}

# Fonction pour convertir et valider l'URL d'entrée
sanitize_input_url() {
    local input=$1
    local sanitized_url

    # Vérifie si l'entrée est vide
    if [ -z "$input" ]; then
        log_message "ERROR" "Input URL is empty"
        return 1
    fi

    # Supprime les guillemets si présents
    sanitized_url=$(echo "$input" | sed -e 's/^["'\'']//' -e 's/["'\'']$//')

    # Vérifie si l'URL contient des caractères de contrôle
    if echo "$sanitized_url" | grep -q '[[:cntrl:]]'; then
        log_message "ERROR" "URL contains control characters"
        return 1
    fi

    # Convertit les séquences d'échappement shell
    sanitized_url=$(printf '%b' "$sanitized_url")

    # Vérifie si l'URL est un format valide basique
    if ! echo "$sanitized_url" | grep -qE '^https?://[^[:space:]]+\.[^[:space:]]+$'; then
        log_message "ERROR" "Invalid URL format: $sanitized_url"
        return 1
    fi

    echo "$sanitized_url"
}

# Fonction de nettoyage d'URL
clean_url() {
    local url=$1
    local cleaned_url

    # Supprime les espaces de début et fin
    cleaned_url=$(echo "$url" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')

    # Remplace les espaces par %20
    cleaned_url=$(echo "$cleaned_url" | sed 's/ /%20/g')

    # Encode les caractères spéciaux courants
    cleaned_url=$(echo "$cleaned_url" | sed \
        -e 's/\[/%5B/g' \
        -e 's/\]/%5D/g' \
        -e 's/(/%28/g' \
        -e 's/)/%29/g' \
        -e 's/\#/%23/g' \
        -e 's/\$/%24/g' \
        -e 's/\&/%26/g' \
        -e 's/\+/%2B/g' \
        -e 's/\,/%2C/g' \
        -e 's/\:/%3A/g' \
        -e 's/\;/%3B/g' \
        -e 's/\=/%3D/g' \
        -e 's/\?/%3F/g' \
        -e 's/\@/%40/g')

    # Préserve les : après http/https
    cleaned_url=$(echo "$cleaned_url" | sed 's|http%3A|http:|g' | sed 's|https%3A|https:|g')

    # Vérifie que l'URL est toujours valide après le nettoyage
    if [[ ! "$cleaned_url" =~ ^https?:// ]]; then
        log_message "ERROR" "URL cleaning resulted in invalid URL: $cleaned_url"
        return 1
    fi

    echo "$cleaned_url"
}

# Fonction de validation d'URL
validate_url() {
    local url=$1
    local type=$2  # "pbf" ou "poly"
    
    # Vérifie si l'URL est vide
    if [ -z "$url" ]; then
        log_message "ERROR" "URL is empty"
        return 1
    fi
    
    # Vérifie si l'URL commence par http:// ou https://
    if [[ ! "$url" =~ ^https?:// ]]; then
        log_message "ERROR" "URL must start with http:// or https://"
        return 1
    fi
    
    # Vérifie le format de l'URL selon le type
    case $type in
        "pbf")
            if [[ ! "$url" =~ \.(osm\.pbf|pbf)$ ]]; then
                log_message "ERROR" "PBF URL must end with .osm.pbf or .pbf"
                return 1
            fi
            ;;
        "poly")
            if [[ ! "$url" =~ \.poly$ ]]; then
                log_message "ERROR" "Poly URL must end with .poly"
                return 1
            fi
            ;;
        *)
            log_message "ERROR" "Invalid URL type specified"
            return 1
            ;;
    esac
    
    return 0
}

# Fonction pour obtenir l'URL du fichier poly à partir de l'URL PBF
get_poly_url() {
    local pbf_url=$1
    local poly_url
    
    # Remplace -latest.osm.pbf par .poly
    if [[ "$pbf_url" == *"-latest.osm.pbf" ]]; then
        poly_url=${pbf_url//-latest.osm.pbf/.poly}
    # Remplace .osm.pbf par .poly
    elif [[ "$pbf_url" == *".osm.pbf" ]]; then
        poly_url=${pbf_url//.osm.pbf/.poly}
    # Remplace .pbf par .poly
    else
        poly_url=${pbf_url//.pbf/.poly}
    fi
    
    echo "$poly_url"
}

# Fonction de téléchargement avec vérification
download_file() {
    local url=$1
    local output=$2
    local description=$3
    local type=$4  # "pbf" ou "poly"
    
    # Nettoie l'URL
    cleaned_url=$(clean_url "$url")
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Failed to clean URL: $url"
        return 1
    fi
    
    # Valide l'URL nettoyée
    if ! validate_url "$cleaned_url" "$type"; then
        return 1
    fi
    
    log_message "INFO" "Downloading ${description} from ${cleaned_url}"
    
    # Vérifie d'abord si l'URL est accessible
    if ! curl --head --silent --fail --max-time 30 "$cleaned_url" > /dev/null; then
        log_message "ERROR" "URL ${cleaned_url} is not accessible (HTTP 404 or other error)"
        return 1
    fi
    
    # Télécharge le fichier avec barre de progression
    if ! curl -L --fail \
              --connect-timeout 60 \
              --max-time ${TIMEOUT} \
              --retry 3 \
              --retry-delay 5 \
              --progress-bar \
              -o "${output}" \
              "${cleaned_url}"; then
        log_message "ERROR" "Failed to download ${description}"
        return 1
    fi
    
    # Vérifie la taille du fichier
    if [ ! -s "${output}" ]; then
        log_message "ERROR" "Downloaded file ${output} is empty"
        return 1
    fi
    
    # Vérifie le type de fichier
    local file_type
    file_type=$(file -b "${output}")
    case $type in
        "pbf")
            if [[ ! "$file_type" =~ "data" && ! "$file_type" =~ "OpenStreetMap" ]]; then
                log_message "ERROR" "Downloaded file is not a valid PBF file"
                return 1
            fi
            ;;
        "poly")
            if [[ ! "$file_type" =~ "ASCII text" ]]; then
                log_message "ERROR" "Downloaded file is not a valid poly file"
                return 1
            fi
            ;;
    esac
    
    log_message "SUCCESS" "Successfully downloaded ${description}"
    return 0
}

# Fonction de nettoyage en cas d'erreur
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_message "ERROR" "Script failed with exit code ${exit_code}"
        if [ -n "$current_dir" ]; then
            cd "$current_dir"
        fi
        # Supprime les fichiers partiellement téléchargés
        if [ -n "$file" ] && [ -f "carte_${land_lower}/${file}" ]; then
            rm -f "carte_${land_lower}/${file}"
        fi
        if [ -n "$file_poly" ] && [ -f "carte_${land_lower}/${file_poly}" ]; then
            rm -f "carte_${land_lower}/${file_poly}"
        fi
    fi
    exit $exit_code
}

# Met en place le gestionnaire d'erreurs
trap cleanup EXIT

# Vérifie les arguments
if [ "$#" -ne 4 ]; then
    log_message "ERROR" "Usage: $0 <land> <id> <type> <url>"
    log_message "ERROR" "Example: $0 'France' '01' 'hiking' 'https://download.geofabrik.de/europe/france-latest.osm.pbf'"
    exit 1
fi

# Récupère les arguments
land=$1
id=$2
type=$3
input_url=$4

# Valide et nettoie l'URL d'entrée
url=$(sanitize_input_url "$input_url")
if [ $? -ne 0 ]; then
    log_message "ERROR" "Failed to validate input URL"
    exit 1
fi

# Test l'URL après sanitization
log_message "INFO" "Validated URL: $url"

# [Le reste du script reste identique...]


# Sauvegarde le répertoire courant
current_dir=$(pwd)

# Initialisation
log_message "INFO" "Starting download process for map: ${land}"
log_message "INFO" "Parameters: ID=${id}, Type=${type}"

# Prépare les noms de fichiers
land_lower=$(echo $land | tr '[:upper:]' '[:lower:]')
land_lower=$(echo $land_lower | tr ' ' _ )
file="${land_lower}.osm.pbf"
file_poly="${land_lower}.poly"

# Nettoie et détermine l'URL du fichier poly
url_poly=$(get_poly_url "$url")

# Vérifie si le répertoire existe
if [ ! -d "carte_${land_lower}" ]; then
    log_message "ERROR" "Directory carte_${land_lower} does not exist"
    exit 1
fi

# Change le répertoire de travail
cd "carte_${land_lower}" || {
    log_message "ERROR" "Failed to change directory to carte_${land_lower}"
    exit 1
}

# Télécharge les fichiers
log_message "INFO" "Starting download of map files"

# Télécharge le fichier .pbf
if ! download_file "$url" "$file" "OSM PBF file" "pbf"; then
    cd "$current_dir"
    exit 1
fi

# Télécharge le fichier .poly
if ! download_file "$url_poly" "$file_poly" "polygon file" "poly"; then
    cd "$current_dir"
    exit 1
fi

# Vérifie les fichiers téléchargés
log_message "INFO" "Verifying downloaded files"
if [ ! -s "$file" ] || [ ! -s "$file_poly" ]; then
    log_message "ERROR" "One or more downloaded files are empty"
    cd "$current_dir"
    exit 1
fi

# Retourne au répertoire initial
cd "$current_dir"

log_message "SUCCESS" "Map download completed successfully"
log_message "INFO" "Downloaded files:"
log_message "INFO" "- ${file} ($(du -h "carte_${land_lower}/${file}" | cut -f1))"
log_message "INFO" "- ${file_poly} ($(du -h "carte_${land_lower}/${file_poly}" | cut -f1))"