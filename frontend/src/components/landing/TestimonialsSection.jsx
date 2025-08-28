import React from 'react';

const TestimonialsSection = () => {
  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Marketing Director",
      content: "CPS has revolutionized our outreach campaigns. We've seen a 300% increase in qualified leads.",
      avatar: "SJ",
    },
    {
      name: "Mike Chen",
      role: "Sales Manager",
      content: "The automation saves us 20+ hours per week. The ROI is incredible.",
      avatar: "MC",
    },
    {
      name: "Emily Davis",
      role: "CEO",
      content: "Best investment we've made for scaling our business development efforts.",
      avatar: "ED",
    },
  ];

  return (
    <section id="testimonials" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">What Our Users Say</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, idx) => (
            <div key={idx} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <p className="text-gray-600 mb-4 italic">"{testimonial.content}"</p>
              <div className="flex items-center">
                <div className="w-10 h-10 bg-indigo-600 text-white rounded-full flex items-center justify-center font-semibold mr-3">
                  {testimonial.avatar}
                </div>
                <div>
                  <p className="font-semibold">{testimonial.name}</p>
                  <p className="text-sm text-gray-500">{testimonial.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;