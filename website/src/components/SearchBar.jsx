export default function SearchBar() {
    return (
      <div className="w-full max-w-xl flex items-center gap-2">
        <input
          type="text"
          placeholder="Try 'slow-burn rivals to lovers in a historical court'..."
          className="w-full px-5 py-3 rounded-full shadow-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-rose-400"
        />
        <button className="bg-rose-500 hover:bg-rose-600 text-white px-5 py-3 rounded-full font-semibold transition">
          Search
        </button>
      </div>
    );
  }
  