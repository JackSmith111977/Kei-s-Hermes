# Detailed Reference

## 三、if __name__ 的正确理解

```python
# ✅ 标准结构
import sys

def main():
    """脚本入口函数"""
    args = sys.argv[1:]
    print(f"参数: {args}")

if __name__ == "__main__":
    main()
```

**为什么需要这个？**
- 当脚本被 `python script.py` 直接运行时，`__name__` = `"__main__"`
- 当脚本被 `import script` 导入时，`__name__` = `"script"`
- 不写这个，import 时也会执行代码

**常见错误：**
```python
# ❌ 错误：直接在最外层写代码
print("Hello")

# ✅ 正确：封装在函数里
def main():
    print("Hello")

if __name__ == "__main__":
    main()
```


> 🔍 **## 四、错误处理最佳实践** and details moved to [references/detailed.md](references/detailed.md)
