import React, { useRef, useState } from 'react'

const ImageUpload = ({ onImageSelect, selectedImage }) => {
  const fileInputRef = useRef(null)
  const [dragActive, setDragActive] = useState(false)

  const handleFile = (file) => {
    if (file && file.type.startsWith('image/')) {
      onImageSelect(file)
    } else {
      alert('Please select a valid image file')
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const formatClassName = (name) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <div className="image-upload-container">
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${selectedImage ? 'has-image' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleChange}
          style={{ display: 'none' }}
        />
        
        {selectedImage ? (
          <div className="image-preview">
            <img
              src={URL.createObjectURL(selectedImage)}
              alt="Selected food"
              className="preview-image"
            />
            <p className="image-name">{formatClassName(selectedImage.name.replace(/\.[^/.]+$/, ''))}</p>
            <button
              className="change-image-btn"
              onClick={(e) => {
                e.stopPropagation()
                fileInputRef.current?.click()
              }}
            >
              Change Image
            </button>
          </div>
        ) : (
          <div className="upload-placeholder">
            <svg
              width="64"
              height="64"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p className="upload-text">Drag & drop an image here</p>
            <p className="upload-subtext">or click to browse</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ImageUpload

