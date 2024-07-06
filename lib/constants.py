binary_extensions = {
    # Images
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".ico", ".webp", ".svg",
    # Audio
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus",
    # Video
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mpg", ".mpeg", ".m4v", ".3gp",
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".odt", ".ods", ".odp", ".pages", ".numbers", ".key",
    # Archives
    ".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz",
    # Executables
    ".exe", ".dll", ".so", ".dylib", ".bin", ".apk", ".app",
    # Disk images
    ".dmg", ".iso", ".img",
    # Design files
    ".psd", ".ai", ".indd", ".sketch",
    # Font files
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    # Programming-specific
    ".pyc", ".class", ".jar", ".war", ".ear",
    # Database files
    ".db", ".sqlite", ".mdb", ".accdb",
    # System files
    ".sys", ".dll", ".drv", ".cab",
    # Other binary formats
    ".dat", ".bin", ".pkg", ".deb", ".rpm",
    ".msi", ".exe", ".bat", ".com",
    # Add any other binary extensions you commonly encounter
}

file_signatures = {
    'application/pdf': ['25504446'],
    'image/jpeg': ['ffd8ff'],
    'image/png': ['89504e47'],
    'image/gif': ['47494638'],
    'image/webp': ['52494646', '57454250'],
    'image/svg+xml': ['3c737667'],
    'application/zip': ['504b0304'],
    'application/x-7z-compressed': ['377abcaf271c'],
    'application/x-tar': ['7573746172'],
    'application/x-rar-compressed': ['526172211a07'],
    'application/gzip': ['1f8b08'],
    'application/x-bzip2': ['425a68'],
    'application/x-executable': ['7f454c46'],
    'application/vnd.microsoft.portable-executable': ['4d5a'],
    'application/x-shockwave-flash': ['435753'],
    'application/x-ms-dos-executable': ['4d5a'],
    'audio/mpeg': ['494433', 'fffb'],
    'audio/wav': ['52494646'],
    'audio/aac': ['fff1', 'fff9'],
    'audio/ogg': ['4f676753'],
    'video/mp4': ['000000', '6674797069736F6D'],
    'video/quicktime': ['0000000c71746D6669'],
    'video/x-msvideo': ['52494646'],
    'video/x-matroska': ['1a45dfa3'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['504b0304'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['504b0304'],
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['504b0304'],
    'application/msword': ['d0cf11e0a1b11ae1'],
    'application/vnd.ms-excel': ['d0cf11e0a1b11ae1'],
    'application/vnd.ms-powerpoint': ['d0cf11e0a1b11ae1'],
    'application/x-sqlite3': ['53514c69746520666f726d6174203300'],
    'application/x-deb': ['213c617263683e'],
    'application/x-rpm': ['edabeedb'],
    'application/x-executable': ['7f454c46'],
    'application/x-sharedlib': ['7f454c46'],
    'application/x-java-applet': ['cafebabe'],
    'application/java-archive': ['504b0304'],
    'application/x-elf': ['7f454c46'],
    'application/vnd.android.package-archive': ['504b0304'],
    'application/x-ms-shortcut': ['4c0000000114020000000000c000000000000046'],
    'font/ttf': ['0001000000'],
    'font/otf': ['4f54544f'],
    'font/woff': ['774f4646'],
    'font/woff2': ['774f4632'],
    'application/x-apple-diskimage': ['7801730d626260'],
    'application/x-iso9660-image': ['4344303031'],
    'application/x-raw-disk-image': ['0000fe00'],
    'application/postscript': ['25215053'],
    'image/vnd.adobe.photoshop': ['38425053'],
    'image/x-icon': ['00000100'],
    'video/x-flv': ['464c5601'],
    'application/x-sqlite3': ['53514c69746520666f726d6174203300'],
    'application/vnd.microsoft.portable-executable': ['4d5a9000'],
    'application/x-mach-binary': ['feedface', 'feedfacf', 'cefaedfe', 'cffaedfe'],
    'application/x-python-code': ['03f30d0a'],
}
