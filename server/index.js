import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import fs from 'fs/promises';
import * as pdfParseModule from 'pdf-parse';
import { fileURLToPath } from 'url';

const pdfParse = pdfParseModule.default ?? pdfParseModule;

const app = express();
const PORT = 5000;

// Get __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configure multer for PDF uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, 'uploads'));
  },
  filename: (req, file, cb) => {
    // Generate unique filename with timestamp
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

// File filter to accept only PDFs
const fileFilter = (req, file, cb) => {
  if (file.mimetype === 'application/pdf') {
    cb(null, true);
  } else {
    cb(new Error('Only PDF files are allowed!'), false);
  }
};

const extractTextFromPDF = async (filePath) => {
  const fileBuffer = await fs.readFile(filePath);
  const parsed = await pdfParse(fileBuffer);
  return parsed.text || '';
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/api/test', (req, res) => {
  res.json({
    message: 'Server running'
  });
});

// PDF upload route
app.post('/api/upload', upload.single('pdf'), async (req, res) => {
  try {
    if (!req.file) {
      console.log('No file uploaded');
      return res.status(400).json({ error: 'No PDF file uploaded' });
    }

    const uploadedPath = req.file.path;
    console.log('File uploaded successfully:', req.file.filename);

    let extractedText = '';
    try {
      extractedText = await extractTextFromPDF(uploadedPath);
      const preview = extractedText.trim().slice(0, 300);
      console.log('Extracted text preview:', preview);

      res.json({
        message: 'PDF uploaded and parsed successfully',
        filename: req.file.filename,
        size: req.file.size,
        preview,
        textLength: extractedText.length
      });
    } catch (parseError) {
      console.error('PDF parsing failed:', parseError);
      return res.status(500).json({ error: 'PDF parsing failed', details: parseError.message });
    }
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Internal server error during upload' });
  }
});

// Upload error handler
app.use((err, req, res, next) => {
  if (!err) return next()
  console.error('Upload middleware error:', err)

  if (err instanceof multer.MulterError) {
    return res.status(400).json({ error: err.message })
  }

  return res.status(400).json({ error: err.message || 'Upload failed' })
})

// Basic health check
app.get('/', (req, res) => {
  res.json({
    status: 'Server is running',
    port: PORT
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
