# dot-20

## python 虚拟环境

- 创建并激活

```bash
python3 -m venv myenv
source myenv/bin/activate
```

- 停用

```bash
deactivate
```

## 自动创建 requirements.txt

```bash
pip freeze > requirements.txt
```

## 通过 requirements.txt 安装依赖

```bash
pip install -r requirements.txt
```

```bash
pip install git+https://github.com/octavei/dota-indexer-db.git
pip install --upgrade git+https://github.com/octavei/dota-indexer-db.git
```
