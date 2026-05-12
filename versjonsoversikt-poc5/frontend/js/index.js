import { API_BASE } from "./script.js";
import { setupFileUpload, loadFiles, showBanner } from "./fileManager.js";

// Oppsett for uploads
setupFileUpload(
    'uploadForm',
    'versjonsoversikt-fil',
    'versjonsoversikt-navn',
    '/upload',
    () => {
        window.location.href = 'endring.html?t=' + Date.now();
    }
);

// Last filer ved oppstart
loadFiles(
    '/list-uploads',
    'file-list',
    '/uploads/',
    '/delete/'
);