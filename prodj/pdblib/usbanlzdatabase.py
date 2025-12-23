import logging

from .usbanlz import AnlzFile

class UsbAnlzDatabase(dict):
  def __init__(self):
    super().__init__(self)
    self.parsed = None

  def get_beatgrid(self):
    if not "beatgrid" in self:
      raise KeyError("UsbAnlzDatabase: no beatgrid found")
    return self["beatgrid"]

  def get_memory_cues(self):
    if not "memory_cues" in self:
      raise KeyError("UsbAnlzDatabase: no memory cue points found")
    return self["memory_cues"]

  def get_hot_cues(self):
    if not "hot_cues" in self:
      raise KeyError("UsbAnlzDatabase: no hot cue points found")
    return self["hot_cues"]

  def get_waveform(self):
    if not "waveform" in self:
      raise KeyError("UsbAnlzDatabase: no waveform found")
    return self["waveform"]

  def get_preview_waveform(self):
    if not "preview_waveform" in self:
      raise KeyError("UsbAnlzDatabase: no preview waveform found")
    return self["preview_waveform"]

  def get_color_preview_waveform(self):
    if not "color_preview_waveform" in self:
      raise KeyError("UsbAnlzDatabase: no color preview waveform found")
    return self["color_preview_waveform"]

  def get_color_waveform(self):
    if not "color_waveform" in self:
      raise KeyError("UsbAnlzDatabase: no color waveform found")
    return self["color_waveform"]

  def collect_entries(self, tag, target):
    obj = next((t for t in self.parsed.tags if t.type == tag), None)
    if obj is None:
      logging.warning("tag %s not found in file", tag)
      return
    self[target] = obj.content.entries

  def collect_cue_points(self):
    if "PCOB" not in [t.type for t in self.parsed.tags]:
      logging.warning("no cue information found in file")
      return
    # Usually there are 2 PCOB entires, one for hot cues and another one for memory cues
    pcob_entries = [t for t in self.parsed.tags if t.type == "PCOB"]
    for entry in pcob_entries:
      if entry.content.type == 'memory':
        self['memory_cues'] = entry.content.entries
        logging.info(f"found {len(entry)} memory cues in DAT file")
      elif entry.content.type == 'hotcue':
        self['hot_cues'] = entry.content.entries
        logging.info(f"found {len(entry)} hot cues in DAT file")

  def _load_file(self, filename):
    with open(filename, "rb") as f:
      self.parsed = AnlzFile.parse_stream(f)

  def _load_buffer(self, data):
    self.parsed = AnlzFile.parse(data)

  def _parse_dat(self):
    logging.debug("Loaded %d tags", len(self.parsed.tags))
    self.collect_entries("PWAV", "preview_waveform")
    self.collect_entries("PQTZ", "beatgrid")
    self.collect_cue_points()
    self.parsed = None

  def _parse_ext(self):
    logging.debug("Loaded %d tags", len(self.parsed.tags))
    self.collect_entries("PWV3", "waveform")
    self.collect_entries("PWV4", "color_preview_waveform")
    self.collect_entries("PWV5", "color_waveform")
    self.parsed = None

  def load_dat_buffer(self, data):
    logging.debug("Loading DAT from buffer")
    self._load_buffer(data)
    self._parse_dat()

  def load_dat_file(self, filename):
    logging.debug("Loading DAT file \"%s\"", filename)
    self._load_file(filename)
    self._parse_dat()

  def load_ext_buffer(self, data):
    logging.debug("Loading EXT from buffer")
    self._load_buffer(data)
    self._parse_ext()

  def load_ext_file(self, filename):
    logging.debug("Loading EXT file \"%s\"", filename)
    self._load_file(filename)
    self._parse_ext()
