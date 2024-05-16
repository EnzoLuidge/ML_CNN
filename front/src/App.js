import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [filterType, setFilterType] = useState('blur');
  const [filteredImage, setFilteredImage] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleFilterChange = (event) => {
    setFilterType(event.target.value);
  };

  const applyFilter = async () => {
    if (!selectedFile) return;

    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64Image = reader.result.split(',')[1];
      
      const response = await fetch('http://localhost:5000/apply_filter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: base64Image, filter: filterType }),
      });
      
      const data = await response.json();
      setFilteredImage(data.filtered_image);
    };
    reader.readAsDataURL(selectedFile);
  };

  return (
    <div className="App">
      <h1>Image Filter with CNN</h1>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <div>
        <label>
          <input type="radio" value="blur" checked={filterType === 'blur'} onChange={handleFilterChange} />
          Blur
        </label>
        <label>
          <input type="radio" value="edge" checked={filterType === 'edge'} onChange={handleFilterChange} />
          Edge Detection
        </label>
        <label>
          <input type="radio" value="sharpen" checked={filterType === 'sharpen'} onChange={handleFilterChange} />
          Sharpen
        </label>
      </div>
      <button onClick={applyFilter}>Apply Filter</button>
      {selectedFile && <img src={URL.createObjectURL(selectedFile)} alt="Original" width="300" />}
      {filteredImage && <img src={`data:image/jpeg;base64,${filteredImage}`} alt="Filtered" width="300" />}
    </div>
  );
}

export default App;
