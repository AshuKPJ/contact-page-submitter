// src/components/landing/BenefitsSection.jsx
import React from 'react';

const BenefitsSection = () => {
  const benefits = [
    "Save hours of manual outreach work",
    "Scale your lead generation efforts",
    "Improve conversion rates with personalization",
    "Track and measure campaign effectiveness",
    "Reduce human error in data entry",
    "Comply with rate limiting and best practices",
  ];

  return (
    <section id="benefits" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">Benefits</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {benefits.map((benefit, idx) => (
            <div key={idx} className="flex items-start">
              <svg className="w-6 h-6 text-green-500 mr-3 mt-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <p className="text-lg text-gray-700">{benefit}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default BenefitsSection;