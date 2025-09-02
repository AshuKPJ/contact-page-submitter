import React, { useState } from "react";
import { 
  User, Mail, Phone, Globe, Building, MapPin, MessageSquare, 
  ChevronRight, Save, CheckCircle, AlertCircle, Briefcase, 
  Hash, FileText, Linkedin, Send, Info, Target, List,
  AlertTriangle, Database, Clock, Zap
} from "lucide-react";

const ContactInformationForm = () => {
  const [activeSection, setActiveSection] = useState("basic");
  const [formData, setFormData] = useState({
    first_name: "Test",
    last_name: "User",
    email: "test@example.com",
    phone_number: "(555) 123-4567",
    company_name: "Tech Solutions Inc",
    job_title: "Marketing Manager"
  });
  const [saveStatus, setSaveStatus] = useState("");

  const sections = [
    {
      id: "basic",
      title: "Essential Fields",
      icon: User,
      description: "Required by 95% of forms",
      priority: "HIGH",
      completionRate: 100,
      fields: [
        { 
          id: "first_name", 
          label: "First Name", 
          type: "text", 
          required: true, 
          icon: User,
          formLabels: ["First Name", "First", "Name", "Your Name"],
          frequency: "98%"
        },
        { 
          id: "last_name", 
          label: "Last Name", 
          type: "text", 
          required: true, 
          icon: User,
          formLabels: ["Last Name", "Last", "Surname"],
          frequency: "98%"
        },
        { 
          id: "email", 
          label: "Email Address", 
          type: "email", 
          required: true, 
          icon: Mail,
          formLabels: ["Email", "Email Address", "E-mail", "Contact Email"],
          frequency: "100%"
        },
        { 
          id: "phone_number", 
          label: "Phone Number", 
          type: "tel", 
          icon: Phone,
          formLabels: ["Phone", "Phone Number", "Contact Number", "Tel"],
          frequency: "75%"
        },
      ]
    },
    {
      id: "company",
      title: "Business Fields",
      icon: Building,
      description: "Common in B2B forms",
      priority: "MEDIUM",
      completionRate: 50,
      fields: [
        { 
          id: "company_name", 
          label: "Company Name", 
          type: "text", 
          icon: Building,
          formLabels: ["Company", "Organization", "Business Name"],
          frequency: "65%"
        },
        { 
          id: "job_title", 
          label: "Job Title", 
          type: "text", 
          icon: Briefcase,
          formLabels: ["Title", "Position", "Role", "Job Title"],
          frequency: "45%"
        },
        { 
          id: "website_url", 
          label: "Company Website", 
          type: "url", 
          icon: Globe,
          formLabels: ["Website", "URL", "Company Website", "Web Address"],
          frequency: "40%"
        },
        { 
          id: "industry", 
          label: "Industry", 
          type: "select",
          options: ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Education", "Other"],
          icon: Hash,
          formLabels: ["Industry", "Sector", "Business Type"],
          frequency: "30%"
        },
      ]
    },
    {
      id: "inquiry",
      title: "Inquiry Details",
      icon: MessageSquare,
      description: "Message and reason fields",
      priority: "HIGH",
      completionRate: 0,
      fields: [
        { 
          id: "subject", 
          label: "Subject/Reason", 
          type: "text", 
          icon: FileText,
          placeholder: "Partnership opportunity",
          formLabels: ["Subject", "Reason for Inquiry", "Topic", "Regarding"],
          frequency: "55%"
        },
        {
          id: "inquiry_type",
          label: "Inquiry Type",
          type: "select",
          options: ["General Inquiry", "Partnership", "Support", "Sales", "Feedback", "Other"],
          icon: List,
          formLabels: ["Reason", "Type", "Category", "Department"],
          frequency: "40%"
        },
        { 
          id: "message", 
          label: "Message Template", 
          type: "textarea", 
          rows: 5, 
          icon: MessageSquare,
          placeholder: "Hi, I'm reaching out regarding a potential partnership opportunity...",
          formLabels: ["Message", "Comments", "Details", "Tell us more", "Your Message"],
          frequency: "95%"
        },
        {
          id: "how_found",
          label: "How Did You Find Us",
          type: "select",
          options: ["Search Engine", "Social Media", "Referral", "Advertisement", "Other"],
          icon: Target,
          formLabels: ["How did you hear about us", "Source", "Referral"],
          frequency: "25%"
        }
      ]
    },
    {
      id: "location",
      title: "Location (Optional)",
      icon: MapPin,
      description: "Rarely required",
      priority: "LOW",
      completionRate: 0,
      fields: [
        { id: "city", label: "City", type: "text", icon: MapPin, frequency: "20%" },
        { id: "state", label: "State/Province", type: "text", icon: MapPin, frequency: "20%" },
        { id: "zip_code", label: "ZIP/Postal Code", type: "text", icon: Hash, frequency: "15%" },
        { 
          id: "country", 
          label: "Country", 
          type: "select",
          options: ["United States", "Canada", "United Kingdom", "Australia", "Other"],
          icon: Globe,
          frequency: "25%"
        },
      ]
    }
  ];

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const handleSave = () => {
    setSaveStatus("saving");
    setTimeout(() => {
      setSaveStatus("saved");
      setTimeout(() => setSaveStatus(""), 3000);
    }, 1500);
  };

  const currentSection = sections.find(s => s.id === activeSection);
  const SectionIcon = currentSection?.icon;

  // Calculate what percentage of forms can be filled
  const calculateFormCoverage = () => {
    const filledFields = Object.keys(formData).filter(key => formData[key]);
    if (filledFields.includes('first_name') && filledFields.includes('email') && filledFields.includes('message')) {
      return 95; // Can fill most forms
    } else if (filledFields.includes('email') && filledFields.includes('message')) {
      return 70; // Can fill basic forms
    }
    return 30; // Limited form filling
  };

  const formCoverage = calculateFormCoverage();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Contact Information</h1>
              <p className="text-gray-600 mt-1">Data for automated form filling across websites</p>
            </div>
            <div className="flex items-center space-x-6">
              {/* Form Coverage Indicator */}
              <div className="text-center">
                <p className="text-sm text-gray-500">Form Coverage</p>
                <div className="flex items-center mt-1">
                  <div className="w-32 bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all ${
                        formCoverage >= 90 ? 'bg-green-500' : 
                        formCoverage >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${formCoverage}%` }}
                    />
                  </div>
                  <span className="ml-2 text-lg font-bold text-gray-700">{formCoverage}%</span>
                </div>
              </div>
              {/* Campaign Readiness */}
              <div className="text-center border-l pl-6">
                <p className="text-sm text-gray-500">Campaign Ready</p>
                <div className="flex items-center justify-center mt-1">
                  {formCoverage >= 70 ? (
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  ) : (
                    <AlertCircle className="w-6 h-6 text-amber-500" />
                  )}
                  <span className="ml-2 font-semibold text-gray-700">
                    {formCoverage >= 70 ? 'Yes' : 'Needs Info'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Warning for large campaigns */}
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-xl p-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
            <div>
              <p className="font-semibold text-amber-900">Large Campaign Detected</p>
              <p className="text-sm text-amber-700 mt-1">
                For CSV files with 100,000+ URLs like yours, split them into chunks of 1,000-2,000 URLs 
                for manageable campaigns (8-16 hours each). Full processing would take weeks.
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-6">
          {/* Sidebar */}
          <div className="w-80 flex-shrink-0">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              {sections.map((section) => {
                const Icon = section.icon;
                const isActive = activeSection === section.id;
                
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full px-4 py-4 flex items-center justify-between transition-all ${
                      isActive 
                        ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-600' 
                        : 'hover:bg-gray-50 border-l-4 border-transparent'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${isActive ? 'bg-blue-100' : 'bg-gray-100'}`}>
                        <Icon className={`w-5 h-5 ${isActive ? 'text-blue-600' : 'text-gray-500'}`} />
                      </div>
                      <div className="text-left">
                        <div className="flex items-center space-x-2">
                          <p className={`text-sm font-medium ${isActive ? 'text-blue-900' : 'text-gray-700'}`}>
                            {section.title}
                          </p>
                          {section.priority === 'HIGH' && (
                            <span className="text-xs px-1.5 py-0.5 bg-red-100 text-red-700 rounded font-semibold">
                              HIGH
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">{section.description}</p>
                        <div className="mt-1 w-20 bg-gray-200 rounded-full h-1">
                          <div 
                            className={`h-1 rounded-full ${section.completionRate === 100 ? 'bg-green-500' : 'bg-blue-500'}`}
                            style={{ width: `${section.completionRate}%` }}
                          />
                        </div>
                      </div>
                    </div>
                    {isActive && <ChevronRight className="w-4 h-4 text-blue-600" />}
                  </button>
                );
              })}
            </div>

            {/* Field Mapping Info */}
            <div className="mt-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Database className="w-5 h-5 text-blue-600" />
                <h3 className="text-sm font-semibold text-blue-900">Smart Field Mapping</h3>
              </div>
              <p className="text-xs text-blue-700 mb-3">
                Our system automatically detects and fills these common form variations:
              </p>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-blue-600">• "Comments" → Message</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-blue-600">• "Full Name" → First + Last</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-blue-600">• "Tel" → Phone Number</span>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              {/* Section Header */}
              <div className="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-md">
                      <SectionIcon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{currentSection?.title}</h2>
                      <p className="text-sm text-gray-600 mt-0.5">{currentSection?.description}</p>
                    </div>
                  </div>
                  {currentSection?.priority && (
                    <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      currentSection.priority === 'HIGH' ? 'bg-red-100 text-red-700' :
                      currentSection.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {currentSection.priority} PRIORITY
                    </div>
                  )}
                </div>
              </div>

              {/* Form Fields */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {currentSection?.fields.map((field) => {
                    const FieldIcon = field.icon;
                    
                    return (
                      <div key={field.id} className={field.type === 'textarea' ? 'md:col-span-2' : ''}>
                        <div className="flex items-center justify-between mb-2">
                          <label className="block text-sm font-medium text-gray-700">
                            {field.label}
                            {field.required && <span className="text-red-500 ml-1">*</span>}
                          </label>
                          {field.frequency && (
                            <span className="text-xs text-gray-500">
                              Found in {field.frequency} of forms
                            </span>
                          )}
                        </div>
                        
                        {field.formLabels && (
                          <p className="text-xs text-gray-500 mb-2">
                            Maps to: {field.formLabels.join(', ')}
                          </p>
                        )}
                        
                        <div className="relative group">
                          <div className="absolute left-3 top-3 text-gray-400 group-focus-within:text-blue-500 transition-colors">
                            <FieldIcon className="w-5 h-5" />
                          </div>
                          
                          {field.type === 'textarea' ? (
                            <textarea
                              id={field.id}
                              rows={field.rows || 4}
                              value={formData[field.id] || ''}
                              onChange={handleChange}
                              className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none transition-all hover:border-gray-400"
                              placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                            />
                          ) : field.type === 'select' ? (
                            <select
                              id={field.id}
                              value={formData[field.id] || ''}
                              onChange={handleChange}
                              className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all hover:border-gray-400 cursor-pointer"
                            >
                              <option value="">Select {field.label}</option>
                              {field.options?.map(opt => (
                                <option key={opt} value={opt}>{opt}</option>
                              ))}
                            </select>
                          ) : (
                            <input
                              type={field.type}
                              id={field.id}
                              value={formData[field.id] || ''}
                              onChange={handleChange}
                              className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all hover:border-gray-400"
                              placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                            />
                          )}
                          
                          {formData[field.id] && (
                            <div className="absolute right-3 top-3">
                              <CheckCircle className="w-5 h-5 text-green-500" />
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Actions */}
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
                <div>
                  {saveStatus === 'saved' && (
                    <div className="flex items-center text-green-600">
                      <CheckCircle className="w-5 h-5 mr-2" />
                      <span className="text-sm font-medium">Information saved!</span>
                    </div>
                  )}
                </div>
                
                <button
                  onClick={handleSave}
                  disabled={saveStatus === 'saving'}
                  className={`px-6 py-2.5 rounded-xl font-medium transition-all flex items-center space-x-2 shadow-lg hover:shadow-xl ${
                    saveStatus === 'saving'
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white'
                  }`}
                >
                  <Save className="w-4 h-4" />
                  <span>{saveStatus === 'saving' ? 'Saving...' : 'Save Information'}</span>
                </button>
              </div>
            </div>

            {/* Stats Card */}
            <div className="mt-6 grid grid-cols-3 gap-4">
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-2">
                  <Clock className="w-5 h-5 text-gray-400" />
                  <span className="text-xs text-gray-500">Processing Time</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">120/hr</p>
                <p className="text-xs text-gray-500">Forms per hour</p>
              </div>
              
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-2">
                  <Zap className="w-5 h-5 text-gray-400" />
                  <span className="text-xs text-gray-500">Success Rate</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">87%</p>
                <p className="text-xs text-gray-500">Forms found</p>
              </div>
              
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-2">
                  <Mail className="w-5 h-5 text-gray-400" />
                  <span className="text-xs text-gray-500">Email Fallback</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">7%</p>
                <p className="text-xs text-gray-500">No form found</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactInformationForm;