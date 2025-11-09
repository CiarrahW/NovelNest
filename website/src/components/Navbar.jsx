import React from "react";

const Navbar = () => {
  return (
    <nav className="w-full bg-white shadow-sm fixed top-0 left-0 z-50">
      <div className="max-w-6xl mx-auto px-6 py-3 flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-[#79D8B8]">NovelNest</h1>
        <div className="flex items-center space-x-4 text-gray-700">
          <button className="bg-gray-100 text-gray-700 px-4 py-1.5 rounded-md text-sm font-medium hover:bg-gray-200 transition">
            Bookshelf
          </button>
          <button className="bg-gray-100 text-gray-700 px-4 py-1.5 rounded-md text-sm font-medium hover:bg-gray-200 transition">
            Profile
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

  