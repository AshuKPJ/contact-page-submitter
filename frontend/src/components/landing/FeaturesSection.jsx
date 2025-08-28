import React from 'react';

const FeaturesSection = () => {
  const features = [
    {
      title: "High-Volume Processing",
      description: "Handle millions of URLs efficiently with parallel processing",
      icon: "🚀",
    },
    {
      title: "Smart CAPTCHA Bypass",
      description: "Integrated DeathByCaptcha support for seamless automation",
      icon: "🔓",
    },
    {
      title: "Fallback Logic",
      description: "Automatically extract emails when forms aren't available",
      icon: "📧",
    },
    {
      title: "Role-Based Access",
      description: "User, Admin, and Owner roles with tailored permissions",
      icon: "👥",
    },
    {
      title: "Detailed Analytics",
      description: "Comprehensive charts and logs for tracking performance",
      icon: "📊",
    },
    {
      title: "API Integration",
      description: "RESTful API for programmatic access and automation",
      icon: "🔌",
    },
  ];

  return (
    <section id="features" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">Powerful Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <div key={idx} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="text-3xl mb-4">{feature.icon}</div>
              <h3 className="font-semibold text-xl mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;