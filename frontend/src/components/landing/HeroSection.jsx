import React from 'react';

const HeroSection = () => {
  return (
    <section className="relative bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
          Automated Outreach at Scale
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Process millions of websites, identify contact forms, and deliver personalized messages with intelligent CAPTCHA bypass integration.
        </p>
        <div className="flex gap-4 justify-center">
          <a href="#features" className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 transition">
            Learn More
          </a>
          <a href="#steps" className="bg-white text-indigo-600 px-8 py-3 rounded-lg border-2 border-indigo-600 hover:bg-indigo-50 transition">
            How It Works
          </a>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;