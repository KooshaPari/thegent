package main

import (
	"archive/zip"
	"bytes"
	"compress/flate"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"nvms/lib"
	"nvms/models"
	"strings"

	spinhttp "github.com/fermyon/spin/sdk/go/v2/http"
)

func getArchiveURL(archiveURL string) string {
    fmt.Println("Archive URL: ", archiveURL)
    splitURL := strings.Split(archiveURL, "/{")
    if len(splitURL) > 1 {
        return splitURL[0] + "/zipball"
    }
    return archiveURL
}
func getRootDir(fileMap map[string][]byte) (string, error) {
	for key := range fileMap {
		// Split the key into parts using "/" as the delimiter
		parts := strings.Split(key, "/")
		if len(parts) > 1 {
			// Return the first part (root directory)
			return parts[0] + "/", nil
		}
	}
	return "", fmt.Errorf("no valid root directory found")
}
func InitializeZipManually() {
	fmt.Println("Manually initializing archive/zip package...")
	

	zip.RegisterDecompressor(zip.Store, io.NopCloser)
	zip.RegisterDecompressor(zip.Deflate, newFlateReader)
	fmt.Println("archive/zip package manually initialized.")
}

func newFlateReader(r io.Reader) io.ReadCloser {
	return flate.NewReader(r)
}
func init() {
    spinhttp.Handle(func(w http.ResponseWriter, r *http.Request) {
        fmt.Println("Received request")
        InitializeZipManually()
        var project models.Project
        fmt.Println("Reading request body...")
        body, err := io.ReadAll(r.Body)
        if err != nil {
            fmt.Println("Error reading request body: ", err)
            http.Error(w, "Error reading request body", http.StatusInternalServerError)
            return
        }
        defer r.Body.Close()
        fmt.Println("Parsing JSON...")
        err = json.Unmarshal(body, &project)
        if err != nil {
            http.Error(w, "Error parsing JSON", http.StatusBadRequest)
            return
        }
        fmt.Println("Decoding user access token...")
        authToken, err := lib.DecryptSecret(project.User.Git.Token)
        if err != nil {
            fmt.Println("Failed to decrypt user access token: ", err)
            http.Error(w, "Failed to decrypt user access token: " + err.Error(), http.StatusInternalServerError)
            return
        }
        fmt.Println("Getting archive URL...") 
        fileURL := project.Repository.HTMLURL+"/contents"
        nvmsFileContent, err := DownloadFile(w, r, fileURL+"/odin.nvms", authToken)
        if err != nil {
            fmt.Println("Error downloading NVMS file: ", err)
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        readMeContent , err := DownloadFile(w, r, fileURL+"/README.md", authToken)
        if err != nil {
            fmt.Println("Error downloading README file: ", err)
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        
        archiveURL := getArchiveURL(project.Repository.ArchiveURL)
        fmt.Println("Initial Archive URL: ", archiveURL)

        projectZipPath, err := DownloadRepo(w, r, archiveURL, authToken)
        if err != nil {
            fmt.Println("Error downloading zip file: ", err)
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        } 
        fmt.Println("Processing zip file...")



        /*nvmsFileContent, readMeContent,projectZip, err := processZip(zipResp, w,r)
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }*/
        fmt.Println("Extracted files")
     
        if(nvmsFileContent == "" || readMeContent == "" || projectZipPath == nil){
            http.Error(w, "Failed to extract files", http.StatusInternalServerError)
            return
        }
        response := map[string]interface{}{
            "NVMSFile": nvmsFileContent,
            "README": readMeContent,
            "ZipBall": projectZipPath,
        }

        w.Header().Set("Content-Type", "application/json")
        if err := json.NewEncoder(w).Encode(response); err != nil {
            http.Error(w, "Failed to encode response", http.StatusInternalServerError)
            return
        }
    })
}

func processZip(zipResp *http.Response, w http.ResponseWriter, r *http.Request) ( string, string, []byte, error) {
    fmt.Println("Processing zip file...")
    var readMeContent []byte; var nvmsContent []byte;
    zipBytes, err := io.ReadAll(zipResp.Body)
        if err != nil {
            http.Error(w, fmt.Sprintf("Failed to read zip file: %v", err), http.StatusInternalServerError)
        }
        if len(zipBytes) == 0 {
            http.Error(w, "Received empty zip file", http.StatusInternalServerError)
        }
        zipReader, err := zip.NewReader(bytes.NewReader(zipBytes), int64(len(zipBytes)))
        if err != nil {
            http.Error(w, fmt.Sprintf("Failed to read zip archive: %v", err), http.StatusInternalServerError)
        }
        for _, file := range zipReader.File {
            if(strings.Contains(strings.ToLower(file.Name), "readme.md")){
                f, err := file.Open()
                if err != nil {
                    return "","",nil, fmt.Errorf("failed to open file %s: %w", file.Name, err)
                }

                readMeContent, err = io.ReadAll(f)
                if err != nil {
                    return "","", nil, fmt.Errorf("failed to read file %s: %w", file.Name, err)
                }
                f.Close()
            }
            
            if strings.Contains(strings.ToLower(file.Name), "odin.nvms"){
                f, err := file.Open()
                if err != nil {
                    return "","",nil, fmt.Errorf("failed to open file %s: %w", file.Name, err)
                }

                nvmsContent, err = io.ReadAll(f)
                if err != nil {
                    return "","", nil, fmt.Errorf("failed to read file %s: %w", file.Name, err)
                }
                f.Close()
            }
		
        }
        return string(nvmsContent), string(readMeContent), zipBytes, err
}
func DownloadRepo(w http.ResponseWriter, r *http.Request, archiveURL string, authToken string) (string, error) {
    // Create temp file with zip extension
    tmpFile, err := os.CreateTemp("/tmp", "repo-*.zip")
    if err != nil {
        return "", fmt.Errorf("failed to create temp file: %v", err)
    }
    defer tmpFile.Close()
    
    // Initial request
    req, err := http.NewRequest("GET", archiveURL, nil)
    if err != nil {
        return "", fmt.Errorf("failed to create request: %v", err)
    }
    
    req.Header.Add("User-Agent", "Byteport")
    req.Header.Add("Accept", "application/vnd.github+json")
    
    resp, err := spinhttp.Send(req)
    if err != nil {
        return "", fmt.Errorf("failed to get archive: %v", err)
    }
    defer resp.Body.Close()
    
    // Handle response
    var finalResp *http.Response
    switch resp.StatusCode {
    case http.StatusOK:
        finalResp = resp
    case http.StatusFound:
        redirectURL := resp.Header.Get("Location")
        if redirectURL == "" {
            return "", fmt.Errorf("no redirect URL provided")
        }
        
        redirReq, err := http.NewRequest("GET", redirectURL, nil)
        if err != nil {
            return "", fmt.Errorf("failed to create redirect request: %v", err)
        }
        
        finalResp, err = spinhttp.Send(redirReq)
        if err != nil {
            return "", fmt.Errorf("failed to download zip: %v", err)
        }
        defer finalResp.Body.Close()
        
        if finalResp.StatusCode != http.StatusOK {
            return "", fmt.Errorf("failed to download zip, status: %s", finalResp.Status)
        }
    default:
        return "", fmt.Errorf("unexpected status code: %d", resp.StatusCode)
    }
    
    // Copy response body to temp file
    _, err = io.Copy(tmpFile, finalResp.Body)
    if err != nil {
        return "", fmt.Errorf("failed to write zip file: %v", err)
    }
    
    return tmpFile.Name(), nil
}
func DownloadFile(w http.ResponseWriter, r *http.Request, fileURL string, authToken string) (string, error) {
    // Use Spin's HTTP client for the initial request
        req,err := http.NewRequest("GET", fileURL, nil)
        if err != nil {
            http.Error(w, fmt.Sprintf("Failed to create request: %v", err), http.StatusInternalServerError)
         
        }
        req.Header.Add("User-Agent", "Byteport") // Set user agent  
        //req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", authToken)) // Add token to headers
        req.Header.Add("Accept", "application/vnd.github+json") // Set accept header to GitHub API
        //fmt.Println("HEAD: ", req.Header)
        // print out full request
        //fmt.Println("Request: ", req)
        resp, err := spinhttp.Send(req)
        if err != nil {
            http.Error(w, fmt.Sprintf("Failed to get archive: %v", err), http.StatusInternalServerError)
        
        }
        defer resp.Body.Close()
        fmt.Println("Checking for Redirect...")
        fmt.Println("Status: ", resp.StatusCode)
 
        var zipResp *http.Response
        if resp.StatusCode != http.StatusFound && resp.StatusCode != http.StatusOK {
            http.Error(w, fmt.Sprintf("Expected redirect or file, got: %s", resp.Status), resp.StatusCode)
           
        }
        if(resp.StatusCode == http.StatusFound){
            fmt.Println("Found, Redirecting...")
            // Get redirect URL from Location header
            redirectURL := resp.Header.Get("Location")
            if redirectURL == "" {
                http.Error(w, "No redirect URL provided", http.StatusInternalServerError)
              
            }

            fmt.Println("Redirect URL: ", redirectURL)
            redirReq, err := http.NewRequest("GET", redirectURL, nil)
            zipResp, err := spinhttp.Send(redirReq)
            if err != nil {
                http.Error(w, fmt.Sprintf("Failed to download zip: %v", err), http.StatusInternalServerError)
             
            }
            defer zipResp.Body.Close()

            if zipResp.StatusCode != http.StatusOK {
                http.Error(w, fmt.Sprintf("Failed to download zip, status: %s", zipResp.Status), zipResp.StatusCode)
               
            }
        }else{
            zipResp = resp
        }
         var fileResp GitHubFileResponse
        if err := json.NewDecoder(zipResp.Body).Decode(&fileResp); err != nil {
            return "", err
        }
        
        // Decode base64 content
        contentBytes, err := base64.StdEncoding.DecodeString(fileResp.Content)
        if err != nil {
            return "", err
        }
    
    return string(contentBytes), nil
}
func main() {}
type GitHubFileResponse struct {
    Content  string `json:"content"`
    Encoding string `json:"encoding"`
}