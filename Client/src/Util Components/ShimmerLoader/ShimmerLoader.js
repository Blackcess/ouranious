import "./ShimmerLoader.css"

const ShimmerLoader = () => {
  return (
    <div className="shimmer-grid">
     {/* Name Loader at the top */}
      <div className="name-loader">
        <div className="spinner"></div>
      </div>

      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="shimmer-card">
          {/* Title */}
          <div className="shimmer-line w-60"></div>

          {/* Graph placeholder */}
          <div className="shimmer-box h-32"></div>

          {/* Footer stats */}
          <div className="shimmer-footer">
            <div className="shimmer-line w-24"></div>
            <div className="shimmer-line w-24"></div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ShimmerLoader;