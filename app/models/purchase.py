class Purchase:
    def __init__(self, data):
        self.ID = data.get('ID')
        self.Data = data.get('Data')
        self.Numri = data.get('Numri')
        self.ID_Konsumatorit = data.get('ID_Konsumatorit')
        self.Konsumatori = data.get('Konsumatori')
        self.Komercialisti = data.get('Komercialisti')
        self.Statusi_Faturimit = data.get('Statusi_Faturimit')
        self.Shifra = data.get('Shifra')
        self.Emertimi = data.get('Emertimi')
        self.Njesia_Artik = data.get('Njesia_Artik')
        self.Sasia = data.get('Sasia')
        self.Cmimi = data.get('Cmimi')
        self.InvoiceNo = self.Numri
        self.Value = (self.Cmimi or 0) * (self.Sasia or 0)
        self.PartnerID = self.Konsumatori
        self.TransactionDate = self.Data

    def dict(self):
        return self.__dict__