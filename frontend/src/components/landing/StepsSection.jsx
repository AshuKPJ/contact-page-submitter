import React from 'react';

const StepsSection = () => {
  const steps = [
    { number: "1", title: "Upload CSV", description: "Import your list of website URLs" },
    { number: "2", title: "Automated Processing", description: "System scans for contact forms and emails" },
    { number: "3", title: "Smart Submission", description: "Forms filled and submitted automatically" },
    { number: "4", title: "Track Results", description: "Monitor progress with detailed logs" },
  ];

  return (
    <section id="steps" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {steps.map((step, idx) => (
            <div key={idx} className="text-center">
              <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                {step.number}
              </div>
              <h3 className="font-semibold text-lg mb-2">{step.title}</h3>
              <p className="text-gray-600">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default StepsSection;