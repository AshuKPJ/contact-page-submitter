import React from 'react';

const IntegrationsSection = () => {
  const integrations = [
    "DeathByCaptcha",
    "Google Sheets",
    "Zapier",
    "Webhook Support",
    "REST API",
    "CSV Export",
  ];

  return (
    <section id="integrations" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">Integrations</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
          {integrations.map((integration, idx) => (
            <div key={idx} className="bg-white p-4 rounded-lg text-center shadow-sm border border-gray-200">
              <p className="font-semibold">{integration}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default IntegrationsSection;