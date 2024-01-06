# PandoraNext Proxy

## 说明

代理 PandoraNext 的请求，定制化某些接口返回数据。

## 代理接口

### 1. /backend-api/models

gpt-4 模型响应增加 gpt-4-mobile 模型。

nginx 配置参考：

```
location /backend-api/models {
    proxy_pass http://127.0.0.1:8345;
    include proxy_params;
}
``````

### 2. "/backend-api/conversation/{conversation_id}"

conversation 原数据，当 conversation 的 model 返回 gpt-4 时，返回为 gpt-4-mobile 模型。

> 过 5s 盾后保证可继续使用 gpt-4-mobile 模型。

nginx 配置参考：

```
location ~ ^/backend-api/conversation/[^/]+$ {
    proxy_pass http://127.0.0.1:8345;
    include proxy_params;
}
```

## 其他

自用脚本，简单写下 README.md 。