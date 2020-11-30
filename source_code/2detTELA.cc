// is called from the benchmark files


#include <iostream>
#include <string>


using namespace std;

int main(int argc, char* argv[])
{
    if (argc < 5) {
        cerr << "Usage: " << argv[0] << " --file HOA_FILE --type TYPE_OF_DETERMINISATION" << endl;
        return 1;
    }
    string hoa_file;
    string type;
    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "--file") {
            if (i + 1 < argc) { // Make sure we aren't at the end of argv!
                hoa_file = argv[++i]; // Increment 'i' so we don't get the argument as the next argv[i].
            } else { // Uh-oh, there was no argument to the destination option.
                  cerr << "--file option requires one argument." << endl;
                return 1;
            }  
        } 
        if (std::string(argv[i]) == "--type") {
            if (i + 1 < argc) { // Make sure we aren't at the end of argv!
                hoa_file = argv[++i]; // Increment 'i' so we don't get the argument as the next argv[i].
            } else { // Uh-oh, there was no argument to the destination option.
                  cerr << "--type option requires one argument." << endl;
                return 1;
            }  
        } 

    }
    int states = 200;
    float time = 1.1234;
    int acc = 32;
    int length_old_acc = 12;
    
    cout << " states: " << 200 << " time: " << time << " acc: " << acc << " old_acc: " << 12 <<endl;
    //cout << 10 <<" times more data" << endl;
}