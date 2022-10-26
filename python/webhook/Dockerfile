FROM almir/webhook

COPY hooks.json /etc/webhook/hooks.json
CMD ["-verbose", "-hooks=/etc/webhook/hooks.json", "-hotreload"]