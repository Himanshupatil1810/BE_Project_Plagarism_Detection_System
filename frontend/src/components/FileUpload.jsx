import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X } from 'lucide-react'

const ACCEPTED = {
  'text/plain':                                                  ['.txt'],
  'application/pdf':                                             ['.pdf'],
  'application/msword':                                          ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
}

export default function FileUpload({ file, onFile, onClear }) {
  const onDrop = useCallback(
    (accepted) => { if (accepted[0]) onFile(accepted[0]) },
    [onFile]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxFiles: 1,
    multiple: false,
  })

  return (
    <div
      {...getRootProps()}
      className={`upload-zone ${isDragActive ? 'drag-active' : ''}`}
    >
      <input {...getInputProps()} />

      <div
        className="flex items-center justify-center rounded-2xl mx-auto mb-4"
        style={{ width: 64, height: 64, background: 'var(--accent-dim)' }}
      >
        <Upload size={28} color="var(--accent)" />
      </div>

      {file ? (
        <>
          <div
            className="font-syne font-bold mb-1 text-accent"
            style={{ fontSize: 18 }}
          >
            {file.name}
          </div>
          <div className="text-app2 text-sm">
            {(file.size / 1024).toFixed(1)} KB — Drop a new file or click to change
          </div>
        </>
      ) : (
        <>
          <div className="font-syne font-bold mb-2" style={{ fontSize: 20 }}>
            {isDragActive ? 'Release to upload' : 'Drop your document here'}
          </div>
          <div className="text-app2 text-sm">
            or click to browse files from your computer
          </div>
        </>
      )}

      {/* File type badges */}
      <div className="flex gap-2 justify-center mt-4 flex-wrap">
        {['TXT', 'PDF', 'DOC', 'DOCX'].map((ext) => (
          <span
            key={ext}
            className="font-jetbrains px-3 py-0.5 rounded-full"
            style={{
              fontSize: 11,
              background: 'var(--bg2)',
              border: '1px solid var(--border2)',
              color: 'var(--text2)',
            }}
          >
            {ext}
          </span>
        ))}
      </div>
    </div>
  )
}
