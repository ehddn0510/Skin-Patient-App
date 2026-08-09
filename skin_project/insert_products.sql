INSERT INTO products (name, brand, category, price, original_price, rating, review_count, description, volume, is_popular, is_new, image_url) VALUES
('Moisture Essence', 'Innisfree', 'skincare', 18000, 22000, 4.5, 1230, 'Deep moisture essence with Jeju volcanic water', '150ml', true, false, 'https://picsum.photos/200/200?random=1'),
('Ceramide Moisture Cream', 'Dr.Jart+', 'moisturizer', 32000, 38000, 4.7, 892, 'Strengthens skin barrier with ceramide', '50ml', true, false, 'https://picsum.photos/200/200?random=2'),
('SPF50 Sunscreen', 'Roundlab', 'suncare', 14000, 16000, 4.6, 2150, 'Lightweight sunscreen with Dokdo mineral water', '50ml', true, false, 'https://picsum.photos/200/200?random=3'),
('Vitamin C Serum', 'Amuse', 'serum', 25000, 30000, 4.4, 670, 'Vitamin C derivative for brightening and antioxidant', '30ml', true, true, 'https://picsum.photos/200/200?random=4'),
('Hyaluronic Acid Toner', 'COSRX', 'skincare', 19000, 23000, 4.8, 3200, '7-type hyaluronic acid for hydrated skin', '150ml', true, false, 'https://picsum.photos/200/200?random=5'),
('Retinol Night Cream', 'OliveYoung', 'anti-aging', 28000, 35000, 4.3, 445, 'Pure retinol for wrinkle improvement and elasticity', '50ml', false, true, 'https://picsum.photos/200/200?random=6'),
('Cleansing Foam', 'Cetaphil', 'cleansing', 12000, 14000, 4.6, 1890, 'Gentle cleansing foam for sensitive skin', '200ml', true, false, 'https://picsum.photos/200/200?random=7'),
('Niacinamide Serum', 'The Ordinary', 'serum', 15000, 18000, 4.5, 2780, '10% Niacinamide for pore and sebum control', '30ml', true, false, 'https://picsum.photos/200/200?random=8'),
('Aloe Soothing Gel', 'Nature Republic', 'moisturizer', 8000, 10000, 4.4, 4560, '99% aloe vera soothing and moisturizing gel', '300ml', false, false, 'https://picsum.photos/200/200?random=9'),
('Brightening Ampoule', 'Sulwhasoo', 'serum', 65000, 75000, 4.7, 320, 'Herbal ingredients for skin tone improvement', '20ml', true, false, 'https://picsum.photos/200/200?random=10')
ON CONFLICT DO NOTHING;
