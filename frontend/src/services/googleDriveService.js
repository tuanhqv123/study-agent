// Google Drive API Configuration
const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY || "YOUR_API_KEY";
const GOOGLE_CLIENT_ID =
  import.meta.env.VITE_GOOGLE_CLIENT_ID || "YOUR_CLIENT_ID";
const DISCOVERY_DOC =
  "https://www.googleapis.com/discovery/v1/apis/drive/v3/rest";
const SCOPES = "https://www.googleapis.com/auth/drive.readonly";

// Debug logging
console.log("Google Drive Config:", {
  apiKey: GOOGLE_API_KEY ? "Set" : "Missing",
  clientId: GOOGLE_CLIENT_ID ? "Set" : "Missing",
});

class GoogleDriveService {
  constructor() {
    this.gapi = null;
    this.tokenClient = null;
    this.accessToken = null;
    this.isInitialized = false;
  }

  async initialize() {
    try {
      console.log("Initializing Google Drive service with GIS...");

      // Check if API keys are set
      if (
        GOOGLE_API_KEY === "YOUR_API_KEY" ||
        GOOGLE_CLIENT_ID === "YOUR_CLIENT_ID"
      ) {
        throw new Error("Google API credentials not configured");
      }

      // Wait for gapi to load
      if (!window.gapi) {
        console.log("Waiting for GAPI to load...");
        await new Promise((resolve, reject) => {
          const checkGapi = () => {
            if (window.gapi) {
              console.log("GAPI loaded successfully");
              resolve();
            } else {
              setTimeout(checkGapi, 100);
            }
          };
          setTimeout(() => reject(new Error("GAPI failed to load")), 10000);
          checkGapi();
        });
      }

      this.gapi = window.gapi;

      // Load the client and picker libraries
      console.log("Loading GAPI modules...");
      await new Promise((resolve, reject) => {
        this.gapi.load("client:picker", {
          callback: () => {
            console.log("GAPI modules loaded successfully");
            resolve();
          },
          onerror: (error) => {
            console.error("Failed to load GAPI modules:", error);
            reject(error);
          },
        });
      });

      // Initialize the API client
      console.log("Initializing GAPI client...");
      await this.gapi.client.init({
        apiKey: GOOGLE_API_KEY,
        discoveryDocs: [DISCOVERY_DOC],
      });

      // Initialize the Google Identity Services token client
      if (!window.google || !window.google.accounts) {
        throw new Error("Google Identity Services not loaded");
      }

      this.tokenClient = window.google.accounts.oauth2.initTokenClient({
        client_id: GOOGLE_CLIENT_ID,
        scope: SCOPES,
        callback: (response) => {
          console.log("GIS token response:", response);
          if (response.access_token) {
            this.accessToken = response.access_token;
            this.gapi.client.setToken({
              access_token: response.access_token,
            });
          }
        },
      });

      this.isInitialized = true;
      console.log("Google Drive service initialized successfully with GIS");
      return true;
    } catch (error) {
      console.error("Failed to initialize Google Drive service:", error);
      return false;
    }
  }

  async signIn() {
    if (!this.isInitialized) {
      const initialized = await this.initialize();
      if (!initialized) {
        throw new Error("Failed to initialize Google Drive service");
      }
    }

    return new Promise((resolve, reject) => {
      try {
        // Check if we already have a valid token
        if (this.accessToken) {
          console.log("Already have access token");
          resolve(true);
          return;
        }

        // Set up the callback for token response
        this.tokenClient.callback = (response) => {
          if (response.error) {
            console.error("Token request failed:", response);
            reject(new Error(response.error));
            return;
          }

          console.log("Token received successfully");
          this.accessToken = response.access_token;
          this.gapi.client.setToken({
            access_token: response.access_token,
          });
          resolve(true);
        };

        // Request access token
        console.log("Requesting access token...");
        this.tokenClient.requestAccessToken({ prompt: "consent" });
      } catch (error) {
        console.error("Failed to sign in to Google:", error);
        reject(error);
      }
    });
  }

  // Test function to check Google APIs availability
  testGoogleAPIs() {
    const checks = {
      gapi: !!window.gapi,
      google: !!window.google,
      picker: !!(window.google && window.google.picker),
      accounts: !!(window.google && window.google.accounts),
      apiKey: GOOGLE_API_KEY !== "YOUR_API_KEY",
      clientId: GOOGLE_CLIENT_ID !== "YOUR_CLIENT_ID",
    };

    console.log("Google APIs availability check:", checks);
    return checks;
  }

  async openPicker() {
    try {
      console.log("Opening Google Drive Picker...");

      // Test API availability first
      const apiCheck = this.testGoogleAPIs();
      if (
        !apiCheck.gapi ||
        !apiCheck.google ||
        !apiCheck.picker ||
        !apiCheck.accounts
      ) {
        throw new Error(`Missing Google APIs: ${JSON.stringify(apiCheck)}`);
      }

      await this.signIn();

      if (!this.accessToken) {
        throw new Error("No access token available");
      }

      return new Promise((resolve) => {
        const picker = new window.google.picker.PickerBuilder()
          .enableFeature(window.google.picker.Feature.NAV_HIDDEN)
          .enableFeature(window.google.picker.Feature.MULTISELECT_ENABLED)
          .setDeveloperKey(GOOGLE_API_KEY)
          .setOAuthToken(this.accessToken)
          .addView(window.google.picker.ViewId.DOCS)
          .addView(
            new window.google.picker.DocsView()
              .setIncludeFolders(true)
              .setMimeTypes(
                "application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword"
              )
          )
          .setCallback((data) => {
            console.log("Picker callback:", data);
            if (data.action === window.google.picker.Action.PICKED) {
              resolve(data.docs);
            } else if (data.action === window.google.picker.Action.CANCEL) {
              resolve([]);
            }
          })
          .build();

        picker.setVisible(true);
      });
    } catch (error) {
      console.error("Failed to open Google Drive picker:", error);
      throw error;
    }
  }

  async downloadFile(fileId, fileName) {
    try {
      console.log(`Downloading file ${fileName} (${fileId})`);

      // First get file info to determine the correct MIME type
      const fileInfo = await this.getFileInfo(fileId);
      console.log(`File info:`, fileInfo);

      let mimeType = fileInfo.mimeType;
      let actualFileName = fileName;

      // Handle Google Docs exports
      if (fileInfo.mimeType === "application/vnd.google-apps.document") {
        console.log("Detected Google Doc, exporting as DOCX...");
        const exportResponse = await this.gapi.client.drive.files.export({
          fileId: fileId,
          mimeType:
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        });

        // Handle the export response properly
        let exportData;
        if (typeof exportResponse.body === "string") {
          // Convert base64 or string to binary
          const binaryString = exportResponse.body;
          const bytes = new Uint8Array(binaryString.length);
          for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
          }
          exportData = bytes.buffer;
        } else {
          exportData = exportResponse.body;
        }

        const blob = new Blob([exportData], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        });

        actualFileName = fileName.replace(/\.[^/.]+$/, ".docx");
        console.log(`Created Google Doc export blob:`, {
          size: blob.size,
          type: blob.type,
          fileName: actualFileName,
        });

        return new File([blob], actualFileName, {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        });
      }

      // For regular files, use fetch API for better binary handling
      console.log("Downloading regular file with fetch API...");
      const downloadUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`;

      const fetchResponse = await fetch(downloadUrl, {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      });

      if (!fetchResponse.ok) {
        throw new Error(`HTTP error! status: ${fetchResponse.status}`);
      }

      // Get the actual response as ArrayBuffer for binary files
      const arrayBuffer = await fetchResponse.arrayBuffer();

      console.log(`Downloaded file:`, {
        size: arrayBuffer.byteLength,
        type: mimeType,
        fileName: actualFileName,
      });

      // Convert to blob with correct MIME type
      const blob = new Blob([arrayBuffer], {
        type: mimeType || "application/octet-stream",
      });

      console.log(`Created blob:`, {
        size: blob.size,
        type: blob.type,
      });

      // Create a File object
      return new File([blob], actualFileName, {
        type: blob.type,
      });
    } catch (error) {
      console.error("Failed to download file from Google Drive:", error);
      throw error;
    }
  }

  async getFileInfo(fileId) {
    try {
      console.log(`Getting file info for ${fileId}`);

      const response = await this.gapi.client.drive.files.get({
        fileId: fileId,
        fields: "id,name,mimeType,size,createdTime,modifiedTime",
      });

      return response.result;
    } catch (error) {
      console.error("Failed to get file info from Google Drive:", error);
      throw error;
    }
  }
}

export default new GoogleDriveService();
