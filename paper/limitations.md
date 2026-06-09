# Limitations

The experiments are controlled and synthetic. The learned component is intentionally small: a VQ tokenizer and token transition artifact designed for mechanism isolation.

The repair methods use diagnostics that are available in the controlled setting. If a real deployment has hidden aliasing with no codebook, decode, physical-validity, or pilot-label signal, these repairs may not identify it.

The paper does not provide external benchmark validation, full-scale video-token world-model evaluation, or physical robot deployment evidence. Those are natural follow-up tests after the controlled mechanism is established.

