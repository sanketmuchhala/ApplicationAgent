# 🚀 ApplicationAgent Quick Start Guide

## ✅ **What's Already Working**
- Your profile is created and saved
- All dependencies are installed
- Basic field matching is operational
- Storage system is working

## 🔑 **Step 1: Set Your DeepSeek API Key**

```bash
# Replace 'your_actual_api_key_here' with your real DeepSeek API key
export DEEPSEEK_API_KEY='your_actual_api_key_here'

# Verify it's set
echo $DEEPSEEK_API_KEY
```

**Get your API key from:** [https://platform.deepseek.com](https://platform.deepseek.com)

## 🎯 **Step 2: Start the Server**

```bash
# Make sure you're in the ApplicationAgent directory
cd /Users/sanketmuchhala/Documents/GitHub/ApplicationAgent

# Activate virtual environment
source .venv/bin/activate

# Start the server
python run_server.py
```

## 🧪 **Step 3: Test the System**

### **Option A: Test Basic Functionality**
```bash
# Run the basic tests
python test_basic.py

# Test semantic matching
python test_semantic_matching.py
```

### **Option B: Customize Your Profile**
```bash
# Customize with your real information
python customize_profile.py
```

### **Option C: Start the MCP Server**
```bash
# Start the server for Claude Desktop integration
python run_server.py
```

## 🔧 **Troubleshooting**

### **If the server won't start:**
1. Check if you're in the right directory
2. Make sure virtual environment is activated
3. Verify your DeepSeek API key is set
4. Check the error messages

### **If you get import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### **If you get configuration errors:**
The system will fall back to basic matching mode, which still works for:
- Field matching
- Form analysis
- Profile management
- Basic response generation

## 📋 **What You Can Do Right Now**

Even without the DeepSeek API key, you can:
1. ✅ **Create and manage profiles**
2. ✅ **Analyze job application forms**
3. ✅ **Match form fields to your profile**
4. ✅ **Generate basic responses**
5. ✅ **Store and retrieve data**

## 🎉 **Next Steps**

1. **Set your DeepSeek API key** for enhanced AI features
2. **Start the server** for MCP integration
3. **Test with real job forms** to see the magic in action
4. **Use Claude Desktop** for the full experience

## 💡 **Pro Tips**

- The system works in **basic mode** without API keys
- **DeepSeek integration** adds advanced AI features
- **MCP server** enables Claude Desktop integration
- **Profile customization** makes responses more accurate

---

**Your ApplicationAgent is ready to use! 🚀**
