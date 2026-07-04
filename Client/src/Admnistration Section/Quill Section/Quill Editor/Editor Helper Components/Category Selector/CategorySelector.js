import "./CategorySelector.css"

export function CategorySelect({ categories, value, onChange }) {
  return (
    <div className="category-select">
      {/* <label>
        Category <span className="required">*</span>
      </label> */}

      <select
        value={value ?? ""}
        onChange={e => onChange(Number(e.target.value))}
      >
        <option value="" disabled>
          Select a category
        </option>

        {categories.map(cat => (
          <option key={cat.categoryId} value={cat.categoryId}>
            {cat.name}
          </option>
        ))}
      </select>
    </div>
  );
}