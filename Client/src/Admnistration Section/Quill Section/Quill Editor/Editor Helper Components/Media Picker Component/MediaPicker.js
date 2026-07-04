import "./MediaPicker.css"
import { useEffect, useState } from "react";
// import { uploadImage, listMedia } from "../api/mediaAPIs";
import { uploadImage,listMedia } from "../../APIs/quillEditorAPIs";
import { MdOutlineCloseFullscreen } from "react-icons/md";
import SpinLoader from "../../../../../Util Components/SpinLoader/SpinLoader";


export default function MediaPicker({ onSelect, onClose }) {
  const [media, setMedia] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [err ,setError] = useState(false);


  useEffect(() => {
    async function load() {
      const items = await listMedia();
      setMedia(items);
      // console.log("Media id to insert is",items[0].media_id)
    }
    load();
  }, []);

  async function handleUpload(e) {
    try {
      const file = e.target.files[0];
      if (!file) return;

      setUploading(true);
      const result = await uploadImage(file);
      setMedia((prev) => [result, ...prev]);
      setUploading(false);
      setError(false)
    } catch (error) {
      setUploading(false)
      console.error(error)
      setError(true)
    }
    
  }
  return (
    <div className="media-picker">
      <span className="close-picker-tag" onClick={onClose}><MdOutlineCloseFullscreen/></span>
      <h3>Insert Media</h3>

      <input
        type="file"
        accept="image/*"
        onChange={handleUpload}
        disabled={uploading}
      />
      {
        uploading && <div className="uploading-in-progress">
          <span><SpinLoader/></span>
          <span>uploading...</span>
        </div>
      }

      <div className="media-grid">
        {media.map((m) => (
          <button
            key={m.media_id}
            onClick={() => onSelect(m.media_id)}
          >
            <img src={process.env.REACT_APP_API_BASE_URL + m.url} alt="" />
          </button>
        ))}
      </div>

      <button onClick={onClose}>Cancel</button>
    </div>
  );
}