import React from 'react';

const FAQSection = () => {
  const faqs = [
    {
      question: "How many URLs can I process?",
      answer: "Our system can handle millions of URLs. The only limit is your subscription plan.",
    },
    {
      question: "What happens if a website has CAPTCHA?",
      answer: "We integrate with DeathByCaptcha to automatically solve CAPTCHAs when encountered.",
    },
    {
      question: "Can I customize the messages?",
      answer: "Yes, you can fully customize your outreach messages with dynamic variables.",
    },
    {
      question: "Is there an API available?",
      answer: "Yes, we provide a comprehensive REST API for programmatic access.",
    },
  ];

  return (
    <section id="faq" className="py-20 bg-white">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">Frequently Asked Questions</h2>
        <div className="space-y-6">
          {faqs.map((faq, idx) => (
            <div key={idx} className="border-b border-gray-200 pb-6">
              <h3 className="font-semibold text-lg mb-2">{faq.question}</h3>
              <p className="text-gray-600">{faq.answer}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FAQSection;