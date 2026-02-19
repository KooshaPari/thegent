# information_life API Reference

> **Source**: `src/thegent/agents/information_life.py`

WP-44001: Pure Information Persona Encoding.
Encodes an agent's 'soul' (weights, value vectors, and memory) into a substrate-independent
information format. Allows for migration between model architectures or digital-to-analog bridges.

---

## InformationPersona

Substrate-independent encoding of an agent identity.

### Methods

#### InformationPersona.__init__

```python
__init__(self, agent_id)
```

#### InformationPersona.check_integrity

Calculate the information entropy of the persona encoding.

```python
check_integrity(self)
```

#### InformationPersona.decode_persona

Reconstruct persona from an information stream.

```python
decode_persona(self, encoded_data)
```

#### InformationPersona.encode_persona

WP-44001: Serialize persona into a high-density, portable format.

```python
encode_persona(self)
```

---

## check_integrity

Calculate the information entropy of the persona encoding.

```python
check_integrity(self)
```

---

## decode_persona

Reconstruct persona from an information stream.

```python
decode_persona(self, encoded_data)
```

---

## encode_persona

WP-44001: Serialize persona into a high-density, portable format.

```python
encode_persona(self)
```

---

