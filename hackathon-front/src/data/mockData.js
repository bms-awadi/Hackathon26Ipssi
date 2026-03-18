export const user = {
  name: "Ryma",
  role: "operator"
};

export const suppliers = [
  {
    supplier_id: "sup-001",
    companyName: "ABC Fournitures",
    siret: "83214056700024",
    rib: "FR76XXXXXX1111",
    contact: "contact@abc.com",
    documents: [
      {
        document_id: "doc-001",
        document_type: "facture",
        status: "Traité",
        anomaly: "Aucune",
        date_expiration: null,
        confidence_score: 0.94
      },
      {
        document_id: "doc-002",
        document_type: "attestation",
        status: "En traitement",
        anomaly: "Expiration proche",
        date_expiration: "2026-06-20",
        confidence_score: 0.88
      }
    ]
  },
  {
    supplier_id: "sup-002",
    companyName: "Tunisie Services",
    siret: "52147896300018",
    rib: "FR76XXXXXX2222",
    contact: "contact@tunisie-services.com",
    documents: [
      {
        document_id: "doc-003",
        document_type: "kbis",
        status: "Erreur",
        anomaly: "Document illisible",
        date_expiration: "2026-05-10",
        confidence_score: 0.61
      },
      {
        document_id: "doc-004",
        document_type: "rib",
        status: "Traité",
        anomaly: "Aucune",
        date_expiration: null,
        confidence_score: 0.97
      }
    ]
  },
  {
    supplier_id: "sup-003",
    companyName: "Global BTP",
    siret: "74125896300055",
    rib: "FR76XXXXXX3333",
    contact: "contact@globalbtp.com",
    documents: [
      {
        document_id: "doc-005",
        document_type: "facture",
        status: "Traité",
        anomaly: "Aucune",
        date_expiration: null,
        confidence_score: 0.91
      },
      {
        document_id: "doc-006",
        document_type: "attestation",
        status: "Traité",
        anomaly: "Aucune",
        date_expiration: "2026-09-15",
        confidence_score: 0.89
      }
    ]
  },
  {
    supplier_id: "sup-004",
    companyName: "Tech Solutions Maroc",
    siret: "98765432100099",
    rib: "MA15XXXXXX4444",
    contact: "info@techsolutions.ma",
    documents: [
      {
        document_id: "doc-007",
        document_type: "kbis",
        status: "Traité",
        anomaly: "Aucune",
        date_expiration: "2027-03-10",
        confidence_score: 0.95
      },
      {
        document_id: "doc-008",
        document_type: "facture",
        status: "En traitement",
        anomaly: "Montant suspect",
        date_expiration: null,
        confidence_score: 0.72
      }
    ]
  },
  {
    supplier_id: "sup-005",
    companyName: "Algeria Logistics",
    siret: "12345678900011",
    rib: "DZ12XXXXXX5555",
    contact: "contact@algerialogistics.dz",
    documents: [
      {
        document_id: "doc-009",
        document_type: "rib",
        status: "Traité",
        anomaly: "Aucune",
        date_expiration: null,
        confidence_score: 0.98
      },
      {
        document_id: "doc-010",
        document_type: "attestation",
        status: "Erreur",
        anomaly: "Signature manquante",
        date_expiration: "2026-08-20",
        confidence_score: 0.55
      }
    ]
  }
];

// pour garder la compatibilité temporaire avec certaines pages
export const documents = suppliers.flatMap((supplier) => supplier.documents);

