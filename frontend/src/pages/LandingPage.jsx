// src/pages/LandingPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import { 
  ArrowRight, Zap, Globe, CheckCircle, Upload, Search, Send, 
  BarChart3, Shield, Clock, Users, TrendingUp, DollarSign,
  Mail, Target, Activity, ChevronDown, ChevronRight, Star,
  FileText, MessageSquare, Sparkles, Award, Rocket, Play,
  AlertCircle, Database, Cpu, X, Menu
} from "lucide-react";

const LandingPage = ({ onLogin, onRegister }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [openFaqIndex, setOpenFaqIndex] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    if (user) {
      navigate("/dashboard");
    }

    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [user, navigate]);

  const stats = [
    { value: "2.4M+", label: "Messages Sent" },
    { value: "97%", label: "Success Rate" },
    { value: "120/hr", label: "Processing Speed" },
    { value: "24/7", label: "Automation" }
  ];

  const features = [
    {
      icon: Zap,
      title: "Lightning Fast Processing",
      description: "Process 120 websites per hour with intelligent form detection and submission",
      color: "from-yellow-400 to-orange-500"
    },
    {
      icon: Shield,
      title: "Advanced CAPTCHA Solving",
      description: "Integrated Death By Captcha service handles even the toughest security challenges",
      color: "from-blue-400 to-indigo-500"
    },
    {
      icon: Mail,
      title: "Smart Email Fallback",
      description: "Never miss an opportunity - automatically finds and uses contact emails when forms aren't available",
      color: "from-green-400 to-emerald-500"
    },
    {
      icon: BarChart3,
      title: "Real-Time Analytics",
      description: "Track campaign performance, success rates, and get detailed reports instantly",
      color: "from-purple-400 to-pink-500"
    },
    {
      icon: Globe,
      title: "Universal Compatibility",
      description: "Works with any website, any form type, in any language or framework",
      color: "from-red-400 to-rose-500"
    },
    {
      icon: Database,
      title: "Bulk Processing",
      description: "Upload CSV files with thousands of URLs and let our system handle the rest",
      color: "from-cyan-400 to-blue-500"
    }
  ];

  const processSteps = [
    {
      number: "01",
      title: "Upload Your List",
      description: "Simply upload a CSV file containing website URLs you want to reach",
      icon: Upload,
      color: "bg-indigo-500"
    },
    {
      number: "02",
      title: "Customize Your Message",
      description: "Create personalized messages with dynamic fields for maximum engagement",
      icon: MessageSquare,
      color: "bg-purple-500"
    },
    {
      number: "03",
      title: "Automated Processing",
      description: "Our AI finds contact forms, fills them accurately, and handles CAPTCHAs",
      icon: Cpu,
      color: "bg-pink-500"
    },
    {
      number: "04",
      title: "Track & Optimize",
      description: "Monitor real-time progress and download comprehensive reports",
      icon: Activity,
      color: "bg-green-500"
    }
  ];

  const pricingPlans = [
    {
      name: "Starter",
      price: "$49",
      period: "/month",
      description: "Perfect for small businesses",
      features: [
        "Up to 1,000 submissions/month",
        "Basic analytics",
        "Email support",
        "CSV upload",
        "95% success rate"
      ],
      highlighted: false
    },
    {
      name: "Professional",
      price: "$149",
      period: "/month",
      description: "For growing companies",
      features: [
        "Up to 10,000 submissions/month",
        "Advanced analytics",
        "Priority support",
        "API access",
        "97% success rate",
        "Custom fields",
        "Team collaboration"
      ],
      highlighted: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "",
      description: "Unlimited scale",
      features: [
        "Unlimited submissions",
        "White-label options",
        "Dedicated account manager",
        "Custom integrations",
        "99% success rate",
        "Priority processing",
        "SLA guarantee"
      ],
      highlighted: false
    }
  ];

  const testimonials = [
    {
      name: "Michael Thompson",
      role: "CEO",
      company: "TechVentures Inc",
      image: "/api/placeholder/60/60",
      text: "Contact Page Submitter transformed our outreach strategy. We reached 10,000 potential partners in just one month with a 96% success rate. The ROI is incredible!",
      rating: 5
    },
    {
      name: "Sarah Chen",
      role: "Marketing Director",
      company: "Growth Agency",
      image: "/api/placeholder/60/60",
      text: "The email fallback feature is a game-changer. We never miss connecting with a prospect, even when websites don't have contact forms. Absolutely essential tool!",
      rating: 5
    },
    {
      name: "David Rodriguez",
      role: "Business Development",
      company: "StartupHub",
      image: "/api/placeholder/60/60",
      text: "Simple to use, powerful results. Cut our outreach time by 90% while increasing response rates. The analytics help us optimize our messaging perfectly.",
      rating: 5
    }
  ];

  const faqs = [
    {
      question: "How many websites can I process per campaign?",
      answer: "There's no hard limit on the number of websites per campaign. Our system processes approximately 120 websites per hour, so a campaign with 2,400 URLs would take about 20 hours to complete. For optimal performance, we recommend campaigns of 1,000-5,000 URLs."
    },
    {
      question: "What happens if a website doesn't have a contact form?",
      answer: "Our intelligent fallback system automatically searches for email addresses on the page, including mailto links, contact information sections, and footer details. If an email is found, your message is sent directly to that address instead."
    },
    {
      question: "How do you handle CAPTCHA and security measures?",
      answer: "We've integrated with Death By Captcha, a leading CAPTCHA-solving service. This handles reCAPTCHA, hCaptcha, and other security challenges automatically. For sites with extreme security, we mark them for manual review."
    },
    {
      question: "Can I customize messages for different websites?",
      answer: "Yes! You can use dynamic fields in your message template that automatically personalize content based on the website, company name, or data from your CSV. This ensures each message feels personally crafted."
    },
    {
      question: "Is this compliant with anti-spam regulations?",
      answer: "Our tool is designed for legitimate business outreach. We recommend using it for B2B communications, partnership inquiries, and professional networking. Always ensure your use complies with applicable laws like CAN-SPAM and GDPR."
    },
    {
      question: "What's your success rate?",
      answer: "Our average success rate is 97% for websites with contact forms. The remaining 3% typically includes sites that are offline, have broken forms, or require manual verification. With email fallback, we achieve contact on 99% of accessible websites."
    }
  ];

  return (
    <div className="bg-white text-gray-800">
      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all ${
        scrolled ? 'bg-white shadow-lg' : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img
                className="h-10 w-auto"
                src="/assets/images/CPS_Header_Logo.png"
                alt="Contact Page Submitter"
              />
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-indigo-600 transition">Features</a>
              <a href="#how-it-works" className="text-gray-700 hover:text-indigo-600 transition">How It Works</a>
              <a href="#pricing" className="text-gray-700 hover:text-indigo-600 transition">Pricing</a>
              <a href="#testimonials" className="text-gray-700 hover:text-indigo-600 transition">Testimonials</a>
              <button
                onClick={onLogin}
                className="text-gray-700 hover:text-indigo-600 transition"
              >
                Login
              </button>
              <button
                onClick={onRegister}
                className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-full hover:shadow-lg transition-all transform hover:scale-105"
              >
                Start Free Trial
              </button>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white shadow-lg">
            <div className="px-4 pt-2 pb-4 space-y-2">
              <a href="#features" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Features</a>
              <a href="#how-it-works" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">How It Works</a>
              <a href="#pricing" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Pricing</a>
              <a href="#testimonials" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Testimonials</a>
              <button
                onClick={onLogin}
                className="block w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Login
              </button>
              <button
                onClick={onRegister}
                className="block w-full px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Start Free Trial
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50"></div>
        <div className="absolute inset-0">
          <div className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
          <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-1.5 mb-6 border border-indigo-200 rounded-full bg-white/80 backdrop-blur">
              <Sparkles className="w-4 h-4 text-indigo-600 mr-2" />
              <span className="text-sm font-medium text-indigo-600">Trusted by 500+ companies worldwide</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Automate Your Outreach
              <br />
              <span className="text-4xl md:text-6xl">At Massive Scale</span>
            </h1>
            
            <p className="text-xl md:text-2xl mb-8 text-gray-600 max-w-3xl mx-auto">
              Reach thousands of websites with personalized messages through automated contact form submissions. 
              <span className="font-semibold text-gray-900"> 97% success rate</span> with intelligent fallbacks.
            </p>
            
            {/* Stats */}
            <div className="flex flex-wrap justify-center gap-8 mb-12">
              {stats.map((stat, idx) => (
                <div key={idx} className="text-center">
                  <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-sm text-gray-600">{stat.label}</p>
                </div>
              ))}
            </div>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={onRegister}
                className="group px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-full font-bold text-lg hover:shadow-2xl transition-all transform hover:scale-105 flex items-center justify-center"
              >
                Start Free Trial
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="px-8 py-4 bg-white border-2 border-gray-300 text-gray-700 rounded-full font-bold text-lg hover:border-indigo-600 hover:text-indigo-600 transition-all flex items-center justify-center">
                <Play className="mr-2 w-5 h-5" />
                Watch Demo
              </button>
            </div>
            
            <p className="mt-6 text-sm text-gray-500">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-gray-900">
              Everything You Need For
              <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent"> Successful Outreach</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Powerful features designed to maximize your contact success rate and save countless hours
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div key={idx} className="group relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity blur"></div>
                  <div className="relative bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all border border-gray-100">
                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center mb-4`}>
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                    <h3 className="text-xl font-bold mb-3 text-gray-900">{feature.title}</h3>
                    <p className="text-gray-600">{feature.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-gray-900">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Get started in minutes with our simple 4-step process
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {processSteps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div key={idx} className="relative">
                  {idx < processSteps.length - 1 && (
                    <div className="hidden lg:block absolute top-16 left-full w-full">
                      <ChevronRight className="w-8 h-8 text-gray-300 -ml-4" />
                    </div>
                  )}
                  
                  <div className="text-center">
                    <div className="relative inline-block mb-4">
                      <div className={`w-20 h-20 ${step.color} rounded-2xl flex items-center justify-center`}>
                        <Icon className="w-10 h-10 text-white" />
                      </div>
                      <span className="absolute -top-2 -right-2 bg-white text-gray-900 text-xs font-bold px-2 py-1 rounded-full border-2 border-gray-200">
                        {step.number}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold mb-2 text-gray-900">{step.title}</h3>
                    <p className="text-gray-600">{step.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-gray-900">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the perfect plan for your outreach needs
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, idx) => (
              <div
                key={idx}
                className={`relative rounded-2xl ${
                  plan.highlighted
                    ? 'bg-gradient-to-b from-indigo-500 to-purple-600 p-1'
                    : 'bg-gray-100 p-1'
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-sm font-bold px-4 py-1 rounded-full">
                      MOST POPULAR
                    </span>
                  </div>
                )}
                
                <div className="bg-white rounded-2xl p-8 h-full">
                  <h3 className="text-2xl font-bold mb-2 text-gray-900">{plan.name}</h3>
                  <p className="text-gray-600 mb-4">{plan.description}</p>
                  
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-gray-600">{plan.period}</span>
                  </div>
                  
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, featureIdx) => (
                      <li key={featureIdx} className="flex items-start">
                        <CheckCircle className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <button
                    onClick={onRegister}
                    className={`w-full py-3 px-6 rounded-xl font-bold transition-all ${
                      plan.highlighted
                        ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {plan.name === 'Enterprise' ? 'Contact Sales' : 'Start Free Trial'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-gray-900">
              Loved By Growth Teams Everywhere
            </h2>
            <p className="text-xl text-gray-600">
              Join hundreds of companies scaling their outreach with Contact Page Submitter
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, idx) => (
              <div key={idx} className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-2xl transition-shadow">
                <div className="flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                
                <p className="text-gray-700 mb-6 italic">"{testimonial.text}"</p>
                
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-400 rounded-full mr-4"></div>
                  <div>
                    <p className="font-bold text-gray-900">{testimonial.name}</p>
                    <p className="text-sm text-gray-600">{testimonial.role} at {testimonial.company}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 bg-white">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-gray-900">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know about Contact Page Submitter
            </p>
          </div>
          
          <div className="space-y-4">
            {faqs.map((faq, idx) => (
              <div key={idx} className="bg-gray-50 rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpenFaqIndex(openFaqIndex === idx ? null : idx)}
                  className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-100 transition-colors"
                >
                  <span className="font-semibold text-gray-900">{faq.question}</span>
                  <ChevronDown className={`w-5 h-5 text-gray-500 transition-transform ${
                    openFaqIndex === idx ? 'rotate-180' : ''
                  }`} />
                </button>
                
                {openFaqIndex === idx && (
                  <div className="px-6 pb-4">
                    <p className="text-gray-600">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-4">
            Ready to 10x Your Outreach?
          </h2>
          <p className="text-xl mb-8 text-indigo-100">
            Join 500+ companies using Contact Page Submitter to scale their growth
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={onRegister}
              className="px-8 py-4 bg-white text-indigo-600 rounded-full font-bold text-lg hover:shadow-2xl transition-all transform hover:scale-105"
            >
              Start Your Free Trial
            </button>
            <button className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-full font-bold text-lg hover:bg-white hover:text-indigo-600 transition-all">
              Schedule Demo
            </button>
          </div>
          
          <div className="mt-12 flex justify-center space-x-8">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center">
              <Rocket className="w-5 h-5 mr-2" />
              <span>Setup in 2 minutes</span>
            </div>
            <div className="flex items-center">
              <Award className="w-5 h-5 mr-2" />
              <span>Cancel anytime</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <img
                className="h-12 mb-4"
                src="/assets/images/CPS_footer_logo.png"
                alt="Contact Page Submitter"
              />
              <p className="text-gray-400 mb-4">
                The most effective automated outreach platform for scaling your business connections.
              </p>
              <div className="flex space-x-4">
                <div className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 cursor-pointer">
                  <Globe className="w-5 h-5" />
                </div>
                <div className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 cursor-pointer">
                  <Mail className="w-5 h-5" />
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2">
                <li><a href="#features" className="hover:text-white transition">Features</a></li>
                <li><a href="#pricing" className="hover:text-white transition">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition">API Docs</a></li>
                <li><a href="#" className="hover:text-white transition">Integrations</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#" className="hover:text-white transition">About Us</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
                <li><a href="#" className="hover:text-white transition">Support</a></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-400">
              © 2025 Contact Page Submitter. All rights reserved.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="text-sm hover:text-white transition">Privacy Policy</a>
              <a href="#" className="text-sm hover:text-white transition">Terms of Service</a>
              <a href="#" className="text-sm hover:text-white transition">Cookie Policy</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;