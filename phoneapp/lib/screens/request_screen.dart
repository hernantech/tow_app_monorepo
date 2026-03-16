import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/request_provider.dart';
import '../models/body_shop.dart';
import '../widgets/shop_map.dart';
import 'confirmation_screen.dart';

class RequestScreen extends StatefulWidget {
  const RequestScreen({super.key});

  @override
  State<RequestScreen> createState() => _RequestScreenState();
}

class _RequestScreenState extends State<RequestScreen> {
  final TextEditingController _locationController = TextEditingController();

  @override
  void initState() {
    super.initState();
    final provider = Provider.of<RequestProvider>(context, listen: false);
    _locationController.text = provider.currentLocation;
  }

  @override
  void dispose() {
    _locationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tow Details'),
      ),
      body: Consumer<RequestProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Map
                ShopMap(
                  shops: provider.shops,
                  selectedShop: provider.selectedShop,
                  onShopTapped: (shop) => provider.selectShop(shop),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    _legendDot(Colors.green, 'Partner (Free)'),
                    const SizedBox(width: 16),
                    _legendDot(Colors.red, 'Standard'),
                    const SizedBox(width: 16),
                    _legendDot(Colors.blue, 'Selected'),
                  ],
                ),
                const SizedBox(height: 24),

                // Location input
                const Text(
                  'Where are you?',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _locationController,
                  decoration: InputDecoration(
                    hintText: 'Enter current location or cross streets',
                    prefixIcon: const Icon(Icons.location_on),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onChanged: (val) => provider.setLocation(val),
                ),
                const SizedBox(height: 24),

                // Shop dropdown
                const Text(
                  'Where are we towing to?',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade400),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<BodyShop>(
                      isExpanded: true,
                      hint: const Text('Select a Body Shop'),
                      value: provider.selectedShop,
                      items: provider.shops.map((shop) {
                        return DropdownMenuItem<BodyShop>(
                          value: shop,
                          child: Text(
                            '${shop.name} ${shop.isPartner ? "(Free Tow)" : ""}',
                          ),
                        );
                      }).toList(),
                      onChanged: (shop) => provider.selectShop(shop),
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Pricing card
                if (provider.selectedShop != null)
                  Card(
                    elevation: 0,
                    color: provider.selectedShop!.isPartner
                        ? Colors.green.shade50
                        : Colors.orange.shade50,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(
                        color: provider.selectedShop!.isPartner
                            ? Colors.green.shade200
                            : Colors.orange.shade200,
                      ),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Estimated Total:',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                provider.estimatedPrice == 0
                                    ? 'FREE'
                                    : '\$${provider.estimatedPrice.toStringAsFixed(2)}',
                                style: TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: provider.estimatedPrice == 0
                                      ? Colors.green.shade700
                                      : Colors.black87,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            provider.selectedShop!.isPartner
                                ? 'Partner shop — your tow is completely free!'
                                : 'Standard towing rates apply for non-partner shops.',
                            style: TextStyle(
                              color: Colors.grey.shade700,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            provider.selectedShop!.address,
                            style: TextStyle(
                              color: Colors.grey.shade600,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                const SizedBox(height: 32),
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: provider.isReadyToSubmit
                        ? () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) =>
                                    const ConfirmationScreen(),
                              ),
                            );
                          }
                        : null,
                    style: ElevatedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text(
                      'Confirm Request',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _legendDot(Color color, String label) {
    return Row(
      children: [
        Icon(Icons.location_on, color: color, size: 18),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }
}
