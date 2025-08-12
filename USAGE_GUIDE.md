# 🚀 **ApplicationAgent Usage Guide**

## 📋 **Quick Start**

### **1. Start Your Server**
```bash
cd /Users/sanketmuchhala/Documents/GitHub/ApplicationAgent
source .venv/bin/activate
python run_server.py
```

### **2. Test Your System**
```bash
python test_real_job_form.py
```

---

## 🎯 **Method 1: Direct Form Analysis**

### **For Any Job Application Form:**

#### **Step 1: Get Form HTML**
1. **Go to any job application form** (LinkedIn, Indeed, company career page)
2. **Right-click** on the form
3. **Select "Inspect Element"** or "View Page Source"
4. **Copy the form HTML** (look for `<form>` tags)

#### **Step 2: Analyze with ApplicationAgent**
```bash
# Edit the analyze_job_form.py file
# Replace the sample_html with your real form HTML
python analyze_job_form.py
```

#### **Example Output:**
```
📋 First Name:
   🎯 Type: first_name (100% confidence)
   💾 Your Value: Sanket

📋 Email Address:
   🎯 Type: email (100% confidence)
   💾 Your Value: muchhalasanket@gmail.com

📋 Years of Experience:
   🎯 Type: experience (100% confidence)
   💾 Your Value: 6.0 years
```

---

## 🤖 **Method 2: Claude Desktop Integration**

### **Setup Claude Desktop:**

#### **Step 1: Install Claude Desktop**
- Download from: https://claude.ai/desktop
- Install and open Claude Desktop

#### **Step 2: Add MCP Server**
1. **Open Claude Desktop**
2. **Go to Settings** (gear icon)
3. **Click "Add a server"**
4. **Enter server details:**
   - **Name:** ApplicationAgent
   - **Command:** `python run_server.py`
   - **Directory:** `/Users/sanketmuchhala/Documents/GitHub/ApplicationAgent`

#### **Step 3: Use with Claude**
```
You: "Help me apply to this job. Here's the form: [paste form HTML]"

Claude: "I'll analyze this job application form using your ApplicationAgent profile. 
Let me match the fields to your information:

- First Name: Sanket
- Email: muchhalasanket@gmail.com
- Experience: 6.0 years
- Current Role: AI Engineer at Progressive Insurance
- Skills: Python, TensorFlow, GPT-4, LangChain, RAG, AWS, Azure

Would you like me to help you fill out this form?"
```

---

## 🌐 **Method 3: Real Job Applications**

### **LinkedIn Easy Apply:**

#### **Step 1: Find a Job**
1. **Go to LinkedIn Jobs**
2. **Find a position you want**
3. **Click "Easy Apply"**

#### **Step 2: Use ApplicationAgent**
1. **Copy the form HTML** (right-click → Inspect)
2. **Run analysis:**
   ```bash
   python analyze_job_form.py
   ```
3. **See what ApplicationAgent would fill**
4. **Use the values to fill the form quickly**

### **Company Career Pages:**

#### **Step 1: Navigate to Application**
1. **Go to company career page**
2. **Find job posting**
3. **Click "Apply Now"**

#### **Step 2: Analyze Form**
1. **Copy form HTML**
2. **Run ApplicationAgent analysis**
3. **Get your pre-filled values**

---

## ⚙️ **Advanced Features**

### **1. Customize Your Profile**
```bash
python customize_profile.py
```

**What you can update:**
- Personal information
- Contact details
- Experience and skills
- Salary expectations
- Job preferences

### **2. Add DeepSeek AI Features**
```bash
# Set your DeepSeek API key
export DEEPSEEK_API_KEY='your_api_key_here'

# Restart the server
python run_server.py
```

**Enhanced features:**
- Better field matching
- Intelligent response generation
- Context-aware form analysis

### **3. Test Different Form Types**
```bash
# Test basic functionality
python test_basic.py

# Test semantic matching
python test_semantic_matching.py

# Test with real job form
python test_real_job_form.py
```

---

## 📊 **Your Profile Data**

### **Current Profile:**
- **Name:** Sanket Muchhala
- **Email:** muchhalasanket@gmail.com
- **Phone:** +1-812-778-4451
- **Current Role:** AI Engineer at Progressive Insurance
- **Experience:** 6.0 years
- **Skills:** Python, TensorFlow, GPT-4, LangChain, RAG, AWS, Azure
- **Education:** MS Data Science (Indiana University)
- **Salary Range:** $140,000 - $180,000
- **LinkedIn:** https://linkedin.com/in/sanket-muchhala
- **GitHub:** https://github.com/sanketmuchhala

### **What ApplicationAgent Can Fill:**
✅ **Personal Info:** Name, email, phone, address  
✅ **Professional:** Experience, current role, company  
✅ **Skills:** Technical skills, programming languages  
✅ **Education:** Degrees, institutions, graduation dates  
✅ **Contact:** LinkedIn, GitHub, portfolio URLs  
✅ **Compensation:** Salary expectations, current salary  

---

## 🔧 **Troubleshooting**

### **Server Won't Start:**
```bash
# Check if you're in the right directory
pwd
# Should show: /Users/sanketmuchhala/Documents/GitHub/ApplicationAgent

# Activate virtual environment
source .venv/bin/activate

# Check Python version
python --version
# Should show: Python 3.13.6

# Try running server
python run_server.py
```

### **Profile Not Found:**
```bash
# Recreate your profile
python setup_profile.py
```

### **Field Matching Issues:**
```bash
# Test semantic matching
python test_semantic_matching.py

# Check if all tests pass
python test_basic.py
```

### **Claude Desktop Connection Issues:**
1. **Make sure server is running**
2. **Check server logs for errors**
3. **Verify MCP configuration**
4. **Restart Claude Desktop**

---

## 💡 **Pro Tips**

### **1. Batch Applications**
- **Analyze multiple forms** at once
- **Create templates** for common fields
- **Save time** on repetitive applications

### **2. ATS Optimization**
- **Use consistent formatting**
- **Match job requirements**
- **Include relevant keywords**

### **3. Custom Responses**
- **Tailor cover letters** to specific jobs
- **Highlight relevant experience**
- **Address job requirements**

### **4. Profile Management**
- **Keep profile updated**
- **Add new skills** as you learn them
- **Update experience** regularly

---

## 🎯 **Real-World Examples**

### **Example 1: LinkedIn Application**
```
Form Field: "Years of Experience"
ApplicationAgent: "6.0 years"
Your Action: Type "6" in the field
```

### **Example 2: Company Career Page**
```
Form Field: "Current Company"
ApplicationAgent: "Progressive Insurance"
Your Action: Copy and paste
```

### **Example 3: Cover Letter**
```
Form Field: "Why are you interested?"
ApplicationAgent: "I am excited to apply for this AI/ML Engineer position..."
Your Action: Use as starting point, customize further
```

---

## 🚀 **Next Steps**

1. **Start using with real job forms**
2. **Set up Claude Desktop integration**
3. **Customize your profile further**
4. **Add DeepSeek API key for enhanced features**
5. **Test with different job types**

**Your ApplicationAgent is ready to revolutionize your job search! 🎉**
